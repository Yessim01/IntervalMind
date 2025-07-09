#!/usr/bin/env python3
"""
Скрипт для отправки ежедневных напоминаний IntervalMind
Можно запускать через cron или планировщик задач
"""

import os
import sys
from datetime import date

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(__file__))

from src.models.user import db, User
from src.models.topic import Topic, Repetition
from src.services.notification_service import NotificationService, DailyNotificationScheduler
from src.main import app

def send_daily_reminders():
    """Отправка ежедневных напоминаний"""
    with app.app_context():
        print(f"🕐 Запуск ежедневных напоминаний на {date.today()}")
        
        # Инициализируем сервисы
        notification_service = NotificationService()
        scheduler = DailyNotificationScheduler(notification_service)
        
        # Получаем всех пользователей
        users = User.query.all()
        print(f"👥 Найдено пользователей: {len(users)}")
        
        if not users:
            print("❌ Пользователи не найдены")
            return
        
        # Собираем данные для каждого пользователя
        users_data = []
        today = date.today()
        
        for user in users:
            # Получаем повторения на сегодня и просроченные
            repetitions_query = db.session.query(Repetition, Topic).join(Topic).filter(
                Repetition.scheduled_date <= today,
                Repetition.is_completed == False,
                Topic.user_id == user.id
            ).order_by(Repetition.scheduled_date).all()
            
            repetitions = []
            for repetition, topic in repetitions_query:
                rep_dict = repetition.to_dict()
                rep_dict['topic'] = topic.to_dict()
                rep_dict['is_overdue'] = repetition.scheduled_date < today
                repetitions.append(rep_dict)
            
            users_data.append({
                'user': user.to_dict(),
                'repetitions': repetitions
            })
            
            print(f"📚 {user.username}: {len(repetitions)} повторений")
        
        # Отправляем уведомления
        stats = scheduler.send_daily_reminders(users_data)
        
        print(f"✅ Отправка завершена:")
        print(f"   📧 Email отправлено: {stats['emails_sent']}")
        print(f"   ❌ Email ошибок: {stats['emails_failed']}")
        print(f"   📱 Telegram отправлено: {stats['telegram_sent']}")
        print(f"   ❌ Telegram ошибок: {stats['telegram_failed']}")

def show_today_summary():
    """Показать сводку на сегодня"""
    with app.app_context():
        today = date.today()
        print(f"📊 Сводка на {today}:")
        
        # Общая статистика
        total_users = User.query.count()
        total_topics = Topic.query.count()
        
        # Повторения на сегодня
        today_repetitions = db.session.query(Repetition).join(Topic).filter(
            Repetition.scheduled_date == today,
            Repetition.is_completed == False
        ).count()
        
        # Просроченные повторения
        overdue_repetitions = db.session.query(Repetition).join(Topic).filter(
            Repetition.scheduled_date < today,
            Repetition.is_completed == False
        ).count()
        
        # Пользователи с повторениями на сегодня
        users_with_repetitions = db.session.query(User.id).join(Topic).join(Repetition).filter(
            Repetition.scheduled_date <= today,
            Repetition.is_completed == False
        ).distinct().count()
        
        print(f"   👥 Всего пользователей: {total_users}")
        print(f"   📚 Всего тем: {total_topics}")
        print(f"   📅 Повторений на сегодня: {today_repetitions}")
        print(f"   ⚠️ Просроченных повторений: {overdue_repetitions}")
        print(f"   🔔 Пользователей с уведомлениями: {users_with_repetitions}")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--summary':
            show_today_summary()
        elif sys.argv[1] == '--send':
            send_daily_reminders()
        elif sys.argv[1] == '--help':
            print("Использование:")
            print("  python daily_reminder.py --send     # Отправить уведомления")
            print("  python daily_reminder.py --summary  # Показать сводку")
            print("  python daily_reminder.py --help     # Показать справку")
        else:
            print("Неизвестная команда. Используйте --help для справки.")
    else:
        print("🧠 IntervalMind - Ежедневные напоминания")
        print("Используйте --help для просмотра доступных команд.")
        show_today_summary()

