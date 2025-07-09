#!/usr/bin/env python3
"""
Скрипт инициализации базы данных IntervalMind
Создает таблицы и добавляет тестовые данные
"""

import os
import sys
from datetime import datetime, date, timedelta

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db, User
from src.models.topic import Topic, Repetition
from src.main import app

def init_database():
    """Инициализация базы данных"""
    with app.app_context():
        # Удаляем все таблицы и создаем заново
        db.drop_all()
        db.create_all()
        
        print("✅ База данных инициализирована")
        
        # Создаем тестового пользователя
        test_user = User(
            username='testuser',
            email='test@example.com'
        )
        db.session.add(test_user)
        db.session.flush()  # Получаем ID пользователя
        
        print("✅ Тестовый пользователь создан")
        
        # Создаем тестовые темы
        test_topics = [
            {
                'title': 'Статья 228 УК РФ',
                'content': 'Незаконные приобретение, хранение, перевозка, изготовление, переработка наркотических средств, психотропных веществ или их аналогов, а также незаконные приобретение, хранение, перевозка растений, содержащих наркотические средства или психотропные вещества, либо их частей, содержащих наркотические средства или психотропные вещества.',
                'category': 'law'
            },
            {
                'title': 'Английское слово: Serendipity',
                'content': 'Serendipity [ˌserənˈdɪpɪti] - счастливая случайность, способность делать приятные и неожиданные открытия. Пример: "It was pure serendipity that led me to find this amazing book."',
                'category': 'language'
            },
            {
                'title': 'Дата основания Москвы',
                'content': 'Москва была основана в 1147 году князем Юрием Долгоруким. Первое упоминание о Москве в летописях датируется 4 апреля 1147 года.',
                'category': 'history'
            },
            {
                'title': 'Формула площади круга',
                'content': 'Площадь круга вычисляется по формуле S = πr², где π ≈ 3.14159, r - радиус круга. Также можно записать как S = π(d/2)², где d - диаметр.',
                'category': 'science'
            },
            {
                'title': 'Принцип работы HTTP',
                'content': 'HTTP (HyperText Transfer Protocol) - протокол передачи гипертекста. Работает по модели запрос-ответ между клиентом и сервером. Основные методы: GET, POST, PUT, DELETE. Статусы ответов: 200 (OK), 404 (Not Found), 500 (Internal Server Error).',
                'category': 'science'
            }
        ]
        
        created_topics = []
        for topic_data in test_topics:
            topic = Topic(
                title=topic_data['title'],
                content=topic_data['content'],
                category=topic_data['category'],
                user_id=test_user.id,
                created_at=datetime.utcnow() - timedelta(days=5)  # Создано 5 дней назад
            )
            db.session.add(topic)
            db.session.flush()
            created_topics.append(topic)
        
        print(f"✅ Создано {len(test_topics)} тестовых тем")
        
        # Создаем расписания повторений для каждой темы
        for topic in created_topics:
            repetitions = Repetition.create_repetition_schedule(
                topic.id, 
                start_date=topic.created_at.date()
            )
            
            for repetition in repetitions:
                db.session.add(repetition)
            
            # Отмечаем некоторые повторения как выполненные
            # Для первой темы - выполнено 2 повторения
            if topic == created_topics[0]:
                repetitions[0].is_completed = True
                repetitions[0].completed_date = topic.created_at.date() + timedelta(days=1)
                repetitions[0].difficulty_rating = 4
                
                repetitions[1].is_completed = True
                repetitions[1].completed_date = topic.created_at.date() + timedelta(days=3)
                repetitions[1].difficulty_rating = 3
            
            # Для второй темы - выполнено 1 повторение
            elif topic == created_topics[1]:
                repetitions[0].is_completed = True
                repetitions[0].completed_date = topic.created_at.date() + timedelta(days=1)
                repetitions[0].difficulty_rating = 5
        
        db.session.commit()
        print("✅ Расписания повторений созданы")
        
        # Выводим статистику
        total_topics = Topic.query.count()
        total_repetitions = Repetition.query.count()
        completed_repetitions = Repetition.query.filter_by(is_completed=True).count()
        
        print(f"\n📊 Статистика базы данных:")
        print(f"   Пользователей: {User.query.count()}")
        print(f"   Тем: {total_topics}")
        print(f"   Повторений: {total_repetitions}")
        print(f"   Выполнено: {completed_repetitions}")
        print(f"   Процент выполнения: {round((completed_repetitions/total_repetitions)*100, 1)}%")

def show_database_schema():
    """Показать схему базы данных"""
    print("\n📋 Схема базы данных IntervalMind:")
    print("\n1. Таблица User (Пользователи):")
    print("   - id: INTEGER PRIMARY KEY")
    print("   - username: VARCHAR(80) UNIQUE NOT NULL")
    print("   - email: VARCHAR(120) UNIQUE NOT NULL")
    
    print("\n2. Таблица Topic (Темы):")
    print("   - id: INTEGER PRIMARY KEY")
    print("   - title: VARCHAR(200) NOT NULL")
    print("   - content: TEXT NOT NULL")
    print("   - category: VARCHAR(100) DEFAULT 'general'")
    print("   - created_at: DATETIME DEFAULT CURRENT_TIMESTAMP")
    print("   - user_id: INTEGER FOREIGN KEY -> User.id")
    
    print("\n3. Таблица Repetition (Повторения):")
    print("   - id: INTEGER PRIMARY KEY")
    print("   - topic_id: INTEGER FOREIGN KEY -> Topic.id")
    print("   - repetition_number: INTEGER NOT NULL (1-8)")
    print("   - scheduled_date: DATE NOT NULL")
    print("   - completed_date: DATE NULL")
    print("   - is_completed: BOOLEAN DEFAULT FALSE")
    print("   - difficulty_rating: INTEGER NULL (1-5)")
    
    print("\n🔗 Связи:")
    print("   - User 1:N Topic (один пользователь - много тем)")
    print("   - Topic 1:N Repetition (одна тема - много повторений)")
    
    print("\n⏰ Интервалы повторений:")
    intervals = {
        1: "1 день",
        2: "3 дня", 
        3: "7 дней (1 неделя)",
        4: "21 день (3 недели)",
        5: "42 дня (6 недель)",
        6: "90 дней (3 месяца)",
        7: "180 дней (6 месяцев)",
        8: "365 дней (1 год)"
    }
    
    for num, interval in intervals.items():
        print(f"   Повторение #{num}: {interval}")

if __name__ == '__main__':
    print("🚀 Инициализация базы данных IntervalMind\n")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--schema':
        show_database_schema()
    else:
        init_database()
        print("\n✅ Инициализация завершена!")
        print("\nДля просмотра схемы БД запустите:")
        print("python init_db.py --schema")

