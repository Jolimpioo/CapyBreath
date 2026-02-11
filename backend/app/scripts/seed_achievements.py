"""
SEED SCRIPT - Achievements Padrão
Popula a tabela achievements com dados iniciais

Uso:
    python -m backend.scripts.seed_achievements

Ou via CLI async:
    asyncio run seed_achievements()
"""

import asyncio
from uuid import uuid4
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.models import Base, Achievement
from app.models.achievement import AchievementCategory, AchievementRarity
from app.core.config import settings


# Dados de achievements padrão
DEFAULT_ACHIEVEMENTS = [
    # ==================== SESSIONS ====================
    {
        "name": "🚀 Primeiro Respiro",
        "description": "Complete sua primeira sessão de respiração",
        "category": AchievementCategory.SESSIONS,
        "rarity": AchievementRarity.COMMON,
        "icon": "🚀",
        "points": 10,
        "criteria_type": "total_sessions",
        "criteria_value": 1,
        "is_active": True,
        "is_hidden": False,
        "display_order": 1,
    },
    {
        "name": "🔥 10 Sessões",
        "description": "Complete 10 sessões de respiração",
        "category": AchievementCategory.SESSIONS,
        "rarity": AchievementRarity.COMMON,
        "icon": "🔥",
        "points": 25,
        "criteria_type": "total_sessions",
        "criteria_value": 10,
        "is_active": True,
        "is_hidden": False,
        "display_order": 2,
    },
    {
        "name": "⚡ 50 Sessões",
        "description": "Complete 50 sessões de respiração",
        "category": AchievementCategory.SESSIONS,
        "rarity": AchievementRarity.RARE,
        "icon": "⚡",
        "points": 50,
        "criteria_type": "total_sessions",
        "criteria_value": 50,
        "is_active": True,
        "is_hidden": False,
        "display_order": 3,
    },
    {
        "name": "💯 100 Sessões",
        "description": "Complete 100 sessões de respiração",
        "category": AchievementCategory.SESSIONS,
        "rarity": AchievementRarity.EPIC,
        "icon": "💯",
        "points": 100,
        "criteria_type": "total_sessions",
        "criteria_value": 100,
        "is_active": True,
        "is_hidden": False,
        "display_order": 4,
    },
    {
        "name": "🏆 500 Sessões",
        "description": "Complete 500 sessões de respiração",
        "category": AchievementCategory.SESSIONS,
        "rarity": AchievementRarity.LEGENDARY,
        "icon": "🏆",
        "points": 200,
        "criteria_type": "total_sessions",
        "criteria_value": 500,
        "is_active": True,
        "is_hidden": False,
        "display_order": 5,
    },
    
    # ==================== RETENTION ====================
    {
        "name": "⏱️ Primeiros Segundos",
        "description": "Aguarde 30 segundos na retenção",
        "category": AchievementCategory.RETENTION,
        "rarity": AchievementRarity.COMMON,
        "icon": "⏱️",
        "points": 15,
        "criteria_type": "best_retention_time",
        "criteria_value": 30,
        "is_active": True,
        "is_hidden": False,
        "display_order": 10,
    },
    {
        "name": "⏰ Um Minuto",
        "description": "Aguarde 1 minuto (60 segundos) na retenção",
        "category": AchievementCategory.RETENTION,
        "rarity": AchievementRarity.COMMON,
        "icon": "⏰",
        "points": 25,
        "criteria_type": "best_retention_time",
        "criteria_value": 60,
        "is_active": True,
        "is_hidden": False,
        "display_order": 11,
    },
    {
        "name": "🎯 2 Minutos",
        "description": "Aguarde 2 minutos (120 segundos) na retenção",
        "category": AchievementCategory.RETENTION,
        "rarity": AchievementRarity.RARE,
        "icon": "🎯",
        "points": 50,
        "criteria_type": "best_retention_time",
        "criteria_value": 120,
        "is_active": True,
        "is_hidden": False,
        "display_order": 12,
    },
    {
        "name": "🧘 3 Minutos",
        "description": "Aguarde 3 minutos (180 segundos) na retenção",
        "category": AchievementCategory.RETENTION,
        "rarity": AchievementRarity.RARE,
        "icon": "🧘",
        "points": 75,
        "criteria_type": "best_retention_time",
        "criteria_value": 180,
        "is_active": True,
        "is_hidden": False,
        "display_order": 13,
    },
    {
        "name": "💪 5 Minutos",
        "description": "Aguarde 5 minutos (300 segundos) na retenção",
        "category": AchievementCategory.RETENTION,
        "rarity": AchievementRarity.EPIC,
        "icon": "💪",
        "points": 100,
        "criteria_type": "best_retention_time",
        "criteria_value": 300,
        "is_active": True,
        "is_hidden": False,
        "display_order": 14,
    },
    {
        "name": "👑 Rei da Retenção",
        "description": "Aguarde 10 minutos (600 segundos) na retenção",
        "category": AchievementCategory.RETENTION,
        "rarity": AchievementRarity.LEGENDARY,
        "icon": "👑",
        "points": 200,
        "criteria_type": "best_retention_time",
        "criteria_value": 600,
        "is_active": True,
        "is_hidden": False,
        "display_order": 15,
    },
    
    # ==================== STREAK ====================
    {
        "name": "📅 Começou!",
        "description": "Pratique 3 dias consecutivos",
        "category": AchievementCategory.STREAK,
        "rarity": AchievementRarity.COMMON,
        "icon": "📅",
        "points": 20,
        "criteria_type": "current_streak",
        "criteria_value": 3,
        "is_active": True,
        "is_hidden": False,
        "display_order": 20,
    },
    {
        "name": "🔗 Uma Semana",
        "description": "Pratique 7 dias consecutivos",
        "category": AchievementCategory.STREAK,
        "rarity": AchievementRarity.RARE,
        "icon": "🔗",
        "points": 50,
        "criteria_type": "current_streak",
        "criteria_value": 7,
        "is_active": True,
        "is_hidden": False,
        "display_order": 21,
    },
    {
        "name": "⛓️ Duas Semanas",
        "description": "Pratique 14 dias consecutivos",
        "category": AchievementCategory.STREAK,
        "rarity": AchievementRarity.RARE,
        "icon": "⛓️",
        "points": 75,
        "criteria_type": "current_streak",
        "criteria_value": 14,
        "is_active": True,
        "is_hidden": False,
        "display_order": 22,
    },
    {
        "name": "📈 Um Mês",
        "description": "Pratique 30 dias consecutivos",
        "category": AchievementCategory.STREAK,
        "rarity": AchievementRarity.EPIC,
        "icon": "📈",
        "points": 100,
        "criteria_type": "current_streak",
        "criteria_value": 30,
        "is_active": True,
        "is_hidden": False,
        "display_order": 23,
    },
    {
        "name": "🔥 Máquina de Hábito",
        "description": "Pratique 100 dias consecutivos",
        "category": AchievementCategory.STREAK,
        "rarity": AchievementRarity.LEGENDARY,
        "icon": "🔥",
        "points": 200,
        "criteria_type": "longest_streak",
        "criteria_value": 100,
        "is_active": True,
        "is_hidden": False,
        "display_order": 24,
    },
    
    # ==================== IMPROVEMENT ====================
    {
        "name": "📊 Progresso Pessoal",
        "description": "Melhore seu tempo de retenção",
        "category": AchievementCategory.IMPROVEMENT,
        "rarity": AchievementRarity.COMMON,
        "icon": "📊",
        "points": 15,
        "criteria_type": "best_retention_time",
        "criteria_value": 45,  # Qualquer melhora contínua
        "is_active": True,
        "is_hidden": False,
        "display_order": 30,
    },
    
    # ==================== MILESTONE ====================
    {
        "name": "🦫 CapyBreather",
        "description": "Complete sua primeira semana de prática",
        "category": AchievementCategory.MILESTONE,
        "rarity": AchievementRarity.COMMON,
        "icon": "🦫",
        "points": 30,
        "criteria_type": "total_sessions",
        "criteria_value": 7,  # 7 sessões em uma semana
        "is_active": True,
        "is_hidden": False,
        "display_order": 40,
    },
    {
        "name": "🎖️ Certificado Wim Hof",
        "description": "Combine: 50 sessões + 2 min retenção + 14 dias streak",
        "category": AchievementCategory.MILESTONE,
        "rarity": AchievementRarity.EPIC,
        "icon": "🎖️",
        "points": 150,
        "criteria_type": "total_sessions",
        "criteria_value": 50,  # Critério principal (outros são bonificadores)
        "is_active": True,
        "is_hidden": True,  # Oculto inicialmente, revelado quando perto
        "display_order": 41,
    },
    {
        "name": "🌟 Mestre do Controle",
        "description": "Mantenha uma sequência de 50 dias",
        "category": AchievementCategory.MILESTONE,
        "rarity": AchievementRarity.LEGENDARY,
        "icon": "🌟",
        "points": 250,
        "criteria_type": "longest_streak",
        "criteria_value": 50,
        "is_active": True,
        "is_hidden": True,  # Oculto, revelado quando perto
        "display_order": 42,
    },
]


async def seed_achievements():
    """Popula a tabela achievements com dados padrão"""
    
    # Cria engine e session
    engine = create_async_engine(
        settings.database_url,
        echo=False,
    )
    
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with async_session() as session:
        try:
            # Verifica se achievements já existem
            from sqlalchemy import select, func
            result = await session.execute(
                select(func.count()).select_from(Achievement)
            )
            count = result.scalar()
            
            if count > 0:
                print(f"⚠️  Já existem {count} achievements no banco. Abortando seed.")
                return
            
            print(f"🌱 Iniciando seed de achievements...")
            
            # Cria achievements
            achievements = []
            for data in DEFAULT_ACHIEVEMENTS:
                achievement = Achievement(
                    id=uuid4(),
                    **data,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                achievements.append(achievement)
            
            # Adiciona ao session
            session.add_all(achievements)
            
            # Commit
            await session.commit()
            
            print(f"✅ {len(achievements)} achievements criados com sucesso!")
            print("\n📋 Achievements populados:")
            for ach in achievements:
                print(f"   {ach.icon} {ach.name} ({ach.rarity}) - {ach.points} pts")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Erro ao criar achievements: {e}")
            raise
        
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_achievements())