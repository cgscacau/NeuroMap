import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import asdict
import streamlit as st
from google.cloud import firestore
from google.oauth2 import service_account
from ..core.models import UserAssessment, PersonalityScores, ProfileInsights

logger = logging.getLogger(__name__)

class FirestoreManager:
    """Gerenciador otimizado para operações Firestore"""
    
    def __init__(self):
        self.db = self._initialize_firestore()
        self._cache = {}
        self._cache_ttl = 300  # 5 minutos
    
    def _initialize_firestore(self) -> firestore.Client:
        """Inicializa cliente Firestore com service account"""
        try:
            # Tenta usar service account do secrets
            if "gcp_service_account" in st.secrets:
                key_dict = json.loads(st.secrets["gcp_service_account"])
                creds = service_account.Credentials.from_service_account_info(key_dict)
                return firestore.Client(credentials=creds, project=key_dict["project_id"])
            else:
                # Fallback para credenciais padrão
                return firestore.Client()
        except Exception as e:
            logger.error(f"Erro ao inicializar Firestore: {e}")
            return None
    
    def _get_cache_key(self, collection: str, doc_id: str, query_params: str = "") -> str:
        """Gera chave para cache"""
        return f"{collection}:{doc_id}:{query_params}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Verifica se entrada do cache ainda é válida"""
        return (datetime.now() - cache_entry['timestamp']).seconds < self._cache_ttl
    
    def _set_cache(self, key: str, data: any) -> None:
        """Define entrada no cache"""
        self._cache[key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def _get_cache(self, key: str) -> Optional[any]:
        """Recupera entrada do cache se válida"""
        if key in self._cache and self._is_cache_valid(self._cache[key]):
            return self._cache[key]['data']
        return None
    
    async def save_assessment(
        self, 
        user_id: str, 
        assessment: UserAssessment,
        batch_size: int = 500
    ) -> str:
        """Salva avaliação com operações em lote otimizadas"""
        
        if not self.db:
            raise Exception("Firestore não inicializado")
        
        try:
            # Prepara dados para salvamento
            assessment_data = {
                'user_id': user_id,
                'assessment_id': assessment.assessment_id,
                'answers': assessment.answers,
                'scores': {
                    'disc': assessment.scores.disc,
                    'big_five': assessment.scores.big_five,
                    'mbti_preferences': assessment.scores.mbti_preferences,
                    'mbti_type': assessment.scores.mbti_type,
                    'confidence_scores': assessment.scores.confidence_scores
                },
                'profile_insights': asdict(assessment.profile_insights) if assessment.profile_insights else {},
                'timestamp': assessment.timestamp,
                'completion_time_minutes': assessment.completion_time_minutes,
                'reliability_score': assessment.reliability_score,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            # Usa transação para garantir consistência
            transaction = self.db.transaction()
            
            @firestore.transactional
            def update_in_transaction(transaction):
                # Referência do documento
                doc_ref = self.db.collection('users').document(user_id)\
                                 .collection('assessments').document(assessment.assessment_id)
                
                # Salva avaliação principal
                transaction.set(doc_ref, assessment_data)
                
                # Atualiza estatísticas do usuário
                user_stats_ref = self.db.collection('users').document(user_id)\
                                       .collection('stats').document('summary')
                
                transaction.set(user_stats_ref, {
                    'last_assessment': assessment.timestamp,
                    'total_assessments': firestore.Increment(1),
                    'last_mbti_type': assessment.scores.mbti_type,
                    'assessment_streak': self._calculate_streak(user_id),
                    'updated_at': firestore.SERVER_TIMESTAMP
                }, merge=True)
                
                return doc_ref.id
            
            doc_id = update_in_transaction(transaction)
            
            # Limpa cache relacionado
            self._invalidate_user_cache(user_id)
            
            logger.info(f"Avaliação {assessment.assessment_id} salva para usuário {user_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Erro ao salvar avaliação: {e}")
            raise
    
    async def get_user_assessments(
        self, 
        user_id: str, 
        limit: int = 10,
        include_details: bool = True
    ) -> List[UserAssessment]:
        """Recupera avaliações do usuário com cache inteligente"""
        
        cache_key = self._get_cache_key('user_assessments', user_id, f"limit:{limit}:details:{include_details}")
        cached_result = self._get_cache(cache_key)
        
        if cached_result:
            return cached_result
        
        if not self.db:
            return []
        
        try:
            # Query otimizada com índices
            query = self.db.collection('users').document(user_id)\
                          .collection('assessments')\
                          .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                          .limit(limit)
            
            docs = query.stream()
            assessments = []
            
            for doc in docs:
                data = doc.to_dict()
                
                # Reconstrói objetos
                scores = PersonalityScores(
                    disc=data['scores']['disc'],
                    big_five=data['scores']['big_five'],
                    mbti_preferences=data['scores']['mbti_preferences'],
                    mbti_type=data['scores']['mbti_type'],
                    confidence_scores=data['scores'].get('confidence_scores', {})
                )
                
                insights = None
                if include_details and 'profile_insights' in data:
                    insights_data = data['profile_insights']
                    if insights_data:
                        insights = ProfileInsights(**insights_data)
                
                assessment = UserAssessment(
                    user_id=data['user_id'],
                    assessment_id=data['assessment_id'],
                    answers=data['answers'],
                    scores=scores,
                    profile_insights=insights,
                    timestamp=data['timestamp'],
                    completion_time_minutes=data.get('completion_time_minutes'),
                    reliability_score=data.get('reliability_score')
                )
                
                assessments.append(assessment)
            
            # Cache resultado
            self._set_cache(cache_key, assessments)
            
            return assessments
            
        except Exception as e:
            logger.error(f"Erro ao recuperar avaliações do usuário {user_id}: {e}")
            return []
    
    async def get_latest_assessment(self, user_id: str) -> Optional[UserAssessment]:
        """Recupera a avaliação mais recente do usuário"""
        
        assessments = await self.get_user_assessments(user_id, limit=1, include_details=True)
        return assessments[0] if assessments else None
    
    async def get_assessment_analytics(self, user_id: str) -> Dict:
        """Recupera analytics das avaliações do usuário"""
        
        cache_key = self._get_cache_key('user_analytics', user_id)
        cached_result = self._get_cache(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            assessments = await self.get_user_assessments(user_id, limit=50, include_details=False)
            
            if not assessments:
                return {}
            
            analytics = {
                'total_assessments': len(assessments),
                'assessment_frequency': self._calculate_assessment_frequency(assessments),
                'mbti_type_history': [a.scores.mbti_type for a in assessments],
                'disc_evolution': self._calculate_disc_evolution(assessments),
                'reliability_trend': [a.reliability_score for a in assessments if a.reliability_score],
                'completion_time_avg': self._calculate_avg_completion_time(assessments),
                'first_assessment': assessments[-1].timestamp if assessments else None,
                'last_assessment': assessments[0].timestamp if assessments else None
            }
            
            # Cache por mais tempo (analytics mudam menos)
            self._set_cache(cache_key, analytics)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Erro ao calcular analytics para usuário {user_id}: {e}")
            return {}
    
    async def get_population_benchmarks(self, filters: Dict = None) -> Dict:
        """Recupera benchmarks populacionais para comparação"""
        
        cache_key = self._get_cache_key('population_benchmarks', 'global', str(filters or {}))
        cached_result = self._get_cache(cache_key)
        
        if cached_result:
            return cached_result
        
        try:
            # Query agregada para estatísticas populacionais
            # Nota: Em produção, isso seria pre-computado em uma função Cloud
            
            query = self.db.collection_group('assessments')
            
            # Aplica filtros se fornecidos
            if filters:
                if 'date_range' in filters:
                    start_date, end_date = filters['date_range']
                    query = query.where('timestamp', '>=', start_date)\
                               .where('timestamp', '<=', end_date)
            
            # Limita para performance (em produção usaria aggregation queries)
            query = query.limit(1000)
            
            docs = query.stream()
            
            disc_scores = {'D': [], 'I': [], 'S': [], 'C': []}
            b5_scores = {'O': [], 'C': [], 'E': [], 'A': [], 'N': []}
            mbti_types = []
            
            for doc in docs:
                data = doc.to_dict()
                scores = data.get('scores', {})
                
                # Coleta scores DISC
                disc_data = scores.get('disc', {})
                for key, value in disc_data.items():
                    dimension = key.replace('DISC_', '')
                    if dimension in disc_scores:
                        disc_scores[dimension].append(value)
                
                # Coleta scores Big Five
                b5_data = scores.get('big_five', {})
                for key, value in b5_data.items():
                    dimension = key.replace('B5_', '')
                    if dimension in b5_scores:
                        b5_scores[dimension].append(value)
                
                # Coleta tipos MBTI
                mbti_type = scores.get('mbti_type')
                if mbti_type:
                    mbti_types.append(mbti_type)
            
            # Calcula estatísticas
            benchmarks = {
                'disc_percentiles': {},
                'b5_percentiles': {},
                'mbti_distribution': {},
                'sample_size': len(list(docs))
            }
            
            # Percentis DISC
            for dim, values in disc_scores.items():
                if values:
                    benchmarks['disc_percentiles'][dim] = {
                        'p25': float(np.percentile(values, 25)),
                        'p50': float(np.percentile(values, 50)),
                        'p75': float(np.percentile(values, 75)),
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values))
                    }
            
            # Percentis Big Five
            for dim, values in b5_scores.items():
                if values:
                    benchmarks['b5_percentiles'][dim] = {
                        'p25': float(np.percentile(values, 25)),
                        'p50': float(np.percentile(values, 50)),
                        'p75': float(np.percentile(values, 75)),
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values))
                    }
            
            # Distribuição MBTI
            if mbti_types:
                from collections import Counter
                type_counts = Counter(mbti_types)
                total = len(mbti_types)
                benchmarks['mbti_distribution'] = {
                    type_: (count / total) * 100 
                    for type_, count in type_counts.items()
                }
            
            # Cache por mais tempo (dados populacionais mudam lentamente)
            self._cache[cache_key] = {
                'data': benchmarks,
                'timestamp': datetime.now()
            }
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Erro ao recuperar benchmarks populacionais: {e}")
            return {}
    
    def _calculate_streak(self, user_id: str) -> int:
        """Calcula streak de avaliações do usuário"""
        # Implementação simplificada - em produção seria mais sofisticada
        return 1
    
    def _calculate_assessment_frequency(self, assessments: List[UserAssessment]) -> str:
        """Calcula frequência média de avaliações"""
        if len(assessments) < 2:
            return "Dados insuficientes"
        
        # Calcula intervalos entre avaliações
        intervals = []
        for i in range(len(assessments) - 1):
            delta = assessments[i].timestamp - assessments[i + 1].timestamp
            intervals.append(delta.days)
        
        avg_interval = sum(intervals) / len(intervals)
        
        if avg_interval <= 7:
            return "Semanal"
        elif avg_interval <= 30:
            return "Mensal"
        elif avg_interval <= 90:
            return "Trimestral"
        else:
            return "Esporádica"
    
    def _calculate_disc_evolution(self, assessments: List[UserAssessment]) -> Dict:
        """Calcula evolução dos scores DISC"""
        if len(assessments) < 2:
            return {}
        
        evolution = {}
        latest = assessments[0].scores.disc
        oldest = assessments[-1].scores.disc
        
        for key in latest.keys():
            if key in oldest:
                change = latest[key] - oldest[key]
                evolution[key] = {
                    'change': round(change, 1),
                    'direction': 'increase' if change > 0 else 'decrease' if change < 0 else 'stable'
                }
        
        return evolution
    
    def _calculate_avg_completion_time(self, assessments: List[UserAssessment]) -> Optional[float]:
        """Calcula tempo médio de completude"""
        times = [a.completion_time_minutes for a in assessments if a.completion_time_minutes]
        return sum(times) / len(times) if times else None
    
    def _invalidate_user_cache(self, user_id: str) -> None:
        """Invalida cache relacionado ao usuário"""
        keys_to_remove = [key for key in self._cache.keys() if user_id in key]
        for key in keys_to_remove:
            del self._cache[key]
    
    async def cleanup_old_cache(self, max_age_hours: int = 24) -> None:
        """Limpa entradas antigas do cache"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        keys_to_remove = [
            key for key, entry in self._cache.items()
            if entry['timestamp'] < cutoff
        ]
        for key in keys_to_remove:
            del self._cache[key]
        
        logger.info(f"Cache limpo: {len(keys_to_remove)} entradas removidas")

# Instância global do gerenciador
db_manager = FirestoreManager()
