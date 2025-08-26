"""
Advanced Anonymous Telegram Chat Bot
The most advanced anonymous chat bot with premium features
"""

import os
import logging
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
                      ChatMemberUpdated, WebAppInfo)
from telegram.ext import (Application, CommandHandler, MessageHandler,
                          CallbackQueryHandler, filters, ContextTypes,
                          ChatMemberHandler)
from telegram.constants import ParseMode
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = "7211561601:AAGWRYFXBFrizVjoM6dEZ2_eP-fQs3WyGYE"
OWNER_ID = 6474226725

# Setup advanced logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('advanced_bot.log'),
        logging.StreamHandler()
    ])
logger = logging.getLogger(__name__)

# Advanced storage for chat sessions, user profiles, and analytics
chat_sessions = {}  # Active chat sessions
user_profiles = {}  # User preferences and stats
waiting_queue = []  # Queue for matching users
chat_history = {}  # Chat session history for analytics
banned_users = set()  # Banned user IDs
vip_users = {OWNER_ID}  # VIP users with special privileges

# Advanced features data
interests_categories = [
    "🎮 Gaming", "🎵 Music", "🎬 Movies", "📚 Books", "🏃 Sports", "🍕 Food",
    "✈️ Travel", "💻 Tech", "🎨 Art", "🔬 Science", "📸 Photography",
    "🧠 Psychology"
]

languages = [
    "🇺🇸 English", "🇪🇸 Spanish", "🇫🇷 French", "🇩🇪 German", "🇮🇹 Italian",
    "🇷🇺 Russian", "🇨🇳 Chinese", "🇯🇵 Japanese", "🇰🇷 Korean", "🇮🇳 Hindi",
    "🇧🇷 Portuguese", "🇳🇱 Dutch"
]


class AdvancedAnonymousBot:

    def __init__(self):
        self.application = None
        self.start_time = datetime.now()
        self.total_messages = 0
        self.total_connections = 0

    async def start_command(self, update: Update,
                            context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with advanced UI"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Anonymous"

        # Initialize user profile if new
        if user_id not in user_profiles:
            user_profiles[user_id] = {
                'username': username,
                'join_date': datetime.now(),
                'total_chats': 0,
                'total_messages': 0,
                'interests': [],
                'preferred_language': None,
                'age_range': None,
                'is_vip': user_id in vip_users,
                'last_active': datetime.now(),
                'settings': {
                    'auto_translate': False,
                    'filter_inappropriate': True,
                    'show_typing': True,
                    'allow_voice_messages': True
                }
            }

        welcome_text = f"""
🎭 **Welcome to Advanced Anonymous Chat!**

Hello {username}! Experience the most advanced anonymous chat platform with premium features:

✨ **Premium Features:**
• 🎯 **Interest-based matching** - Find like-minded people
• 🌍 **Language preferences** - Chat in your preferred language  
• 🔄 **Auto-translation** - Break language barriers
• 🎮 **Chat games & activities** - Interactive fun
• 📊 **Smart matching algorithm** - Better connections
• 🛡️ **Advanced moderation** - Safe environment
• 🎁 **Daily rewards** - Earn coins and unlock features
• ⚡ **Instant connections** - No waiting time

**Your Stats:**
👥 Total chats: {user_profiles[user_id]['total_chats']}
💬 Messages sent: {user_profiles[user_id]['total_messages']}
🏆 Status: {'🌟 VIP' if user_profiles[user_id]['is_vip'] else '👤 Regular'}
        """

        keyboard = [[
            InlineKeyboardButton("🚀 Quick Match", callback_data="quick_match"),
            InlineKeyboardButton("🎯 Interest Match",
                                 callback_data="interest_match")
        ],
                    [
                        InlineKeyboardButton("⚙️ Preferences",
                                             callback_data="preferences"),
                        InlineKeyboardButton("🎮 Chat Games",
                                             callback_data="games_menu")
                    ],
                    [
                        InlineKeyboardButton("📊 My Stats",
                                             callback_data="my_stats"),
                        InlineKeyboardButton("🏆 Leaderboard",
                                             callback_data="leaderboard")
                    ],
                    [
                        InlineKeyboardButton("ℹ️ Help & Features",
                                             callback_data="help_advanced"),
                        InlineKeyboardButton("💎 VIP Features",
                                             callback_data="vip_features")
                    ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(welcome_text,
                                        reply_markup=reply_markup,
                                        parse_mode='Markdown')
        user_profiles[user_id]['last_active'] = datetime.now()
        logger.info(f"Advanced start command used by {user_id} ({username})")

    async def handle_callback_query(self, update: Update,
                                    context: ContextTypes.DEFAULT_TYPE):
        """Handle all callback queries with advanced features"""
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        data = query.data

        # Update user activity
        if user_id in user_profiles:
            user_profiles[user_id]['last_active'] = datetime.now()

        if data == "quick_match":
            await self.quick_match(query, context)
        elif data == "interest_match":
            await self.show_interests_menu(query, context)
        elif data == "preferences":
            await self.show_preferences_menu(query, context)
        elif data == "games_menu":
            await self.show_games_menu(query, context)
        elif data == "my_stats":
            await self.show_user_stats(query, context)
        elif data == "leaderboard":
            await self.show_leaderboard(query, context)
        elif data == "help_advanced":
            await self.show_advanced_help(query, context)
        elif data == "vip_features":
            await self.show_vip_features(query, context)
        elif data.startswith("interest_"):
            await self.handle_interest_selection(query, context)
        elif data.startswith("lang_"):
            await self.handle_language_selection(query, context)
        elif data.startswith("game_"):
            await self.handle_game_selection(query, context)
        elif data == "end_chat":
            await self.end_chat_callback(query, context)
        elif data == "report_user":
            await self.report_user_callback(query, context)
        elif data == "share_contact":
            await self.share_contact_callback(query, context)

    async def quick_match(self, query, context):
        """Advanced quick matching with smart algorithm"""
        user_id = query.from_user.id

        if user_id in chat_sessions:
            await query.edit_message_text(
                "🎭 You're already in a chat! Use /end to exit first.")
            return

        # Add user to session
        chat_sessions[user_id] = {
            'status': 'searching',
            'partner': None,
            'start_time': datetime.now(),
            'messages_count': 0,
            'chat_type': 'quick'
        }

        # Smart matching algorithm
        suitable_partners = []
        for uid in waiting_queue:
            if uid != user_id and uid not in banned_users:
                # Prefer users with similar activity levels
                partner_profile = user_profiles.get(uid, {})
                user_profile = user_profiles.get(user_id, {})

                compatibility_score = self.calculate_compatibility(
                    user_profile, partner_profile)
                suitable_partners.append((uid, compatibility_score))

        if suitable_partners:
            # Sort by compatibility and pick the best match
            suitable_partners.sort(key=lambda x: x[1], reverse=True)
            partner_id = suitable_partners[0][0]
            waiting_queue.remove(partner_id)

            # Connect users
            await self.connect_users(user_id, partner_id, context, 'quick')

        else:
            waiting_queue.append(user_id)

            keyboard = [[
                InlineKeyboardButton("🔄 Switch to Interest Match",
                                     callback_data="interest_match")
            ], [
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_search")
            ]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_text(
                "🔍 **Searching for the perfect chat partner...**\n\n"
                "⚡ Using smart matching algorithm\n"
                "🎯 Finding compatible personality\n"
                "⏱️ Average wait time: 30 seconds\n\n"
                "*You'll be notified instantly when matched!*",
                reply_markup=reply_markup,
                parse_mode='Markdown')

    def calculate_compatibility(self, user1_profile, user2_profile):
        """Calculate compatibility score between two users"""
        score = 0

        # Interest compatibility
        user1_interests = set(user1_profile.get('interests', []))
        user2_interests = set(user2_profile.get('interests', []))
        common_interests = len(user1_interests & user2_interests)
        score += common_interests * 10

        # Language compatibility
        if (user1_profile.get('preferred_language') == user2_profile.get(
                'preferred_language')):
            score += 15

        # Activity level compatibility
        user1_activity = user1_profile.get('total_chats', 0)
        user2_activity = user2_profile.get('total_chats', 0)
        activity_diff = abs(user1_activity - user2_activity)
        score += max(0, 10 - activity_diff)

        return score

    async def connect_users(self,
                            user1_id,
                            user2_id,
                            context,
                            chat_type='quick'):
        """Connect two users with advanced features"""
        # Update sessions
        chat_sessions[user1_id].update({
            'status': 'connected',
            'partner': user2_id,
            'chat_type': chat_type
        })
        chat_sessions[user2_id] = {
            'status': 'connected',
            'partner': user1_id,
            'start_time': datetime.now(),
            'messages_count': 0,
            'chat_type': chat_type
        }

        self.total_connections += 1
        user_profiles[user1_id]['total_chats'] += 1
        user_profiles[user2_id]['total_chats'] += 1

        # Advanced connection message with features
        connection_text = """
🎉 **Connected Successfully!**

🎭 You're now chatting anonymously with a stranger!

**Chat Features:**
• 💬 Send text, photos, videos, voice messages
• 🎮 Type '/games' for interactive activities  
• 🔄 Type '/translate' to enable auto-translation
• 📊 Real-time typing indicators
• 🎯 Smart conversation starters

**Quick Actions:**
        """

        keyboard = [[
            InlineKeyboardButton("🎮 Play Games", callback_data="games_menu"),
            InlineKeyboardButton("💡 Conversation Starters",
                                 callback_data="conversation_starters")
        ],
                    [
                        InlineKeyboardButton("📱 Share Contact",
                                             callback_data="share_contact"),
                        InlineKeyboardButton("🚨 Report User",
                                             callback_data="report_user")
                    ],
                    [
                        InlineKeyboardButton("❌ End Chat",
                                             callback_data="end_chat")
                    ]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Send to both users
        for uid in [user1_id, user2_id]:
            chat_id = query.message.chat_id if hasattr(query,
                                                       'message') else uid
            try:
                await context.bot.send_message(chat_id=uid,
                                               text=connection_text,
                                               reply_markup=reply_markup,
                                               parse_mode='Markdown')
            except Exception as e:
                logger.error(f"Error sending connection message to {uid}: {e}")

        logger.info(
            f"Advanced chat connected: {user1_id} <-> {user2_id} (type: {chat_type})"
        )

    async def show_interests_menu(self, query, context):
        """Show interests selection menu"""
        user_id = query.from_user.id
        user_interests = user_profiles[user_id].get('interests', [])

        text = "🎯 **Select Your Interests** (Choose up to 5)\n\n"
        text += "*This helps us find people you'll enjoy talking to!*\n\n"
        text += f"**Selected:** {len(user_interests)}/5\n"

        if user_interests:
            text += f"**Current:** {', '.join(user_interests[:3])}{'...' if len(user_interests) > 3 else ''}\n\n"

        # Create keyboard with interests
        keyboard = []
        for i in range(0, len(interests_categories), 2):
            row = []
            for j in range(2):
                if i + j < len(interests_categories):
                    category = interests_categories[i + j]
                    emoji = "✅" if category in user_interests else ""
                    button_text = f"{emoji} {category}" if emoji else category
                    row.append(
                        InlineKeyboardButton(button_text,
                                             callback_data=f"interest_{i+j}"))
            keyboard.append(row)

        # Action buttons
        keyboard.extend([[
            InlineKeyboardButton("🚀 Start Matching",
                                 callback_data="start_interest_match")
        ],
                         [
                             InlineKeyboardButton("🔙 Back to Main",
                                                  callback_data="back_to_main")
                         ]])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      reply_markup=reply_markup,
                                      parse_mode='Markdown')

    async def handle_interest_selection(self, query, context):
        """Handle interest selection/deselection"""
        user_id = query.from_user.id
        interest_idx = int(query.data.split('_')[1])
        interest = interests_categories[interest_idx]

        user_interests = user_profiles[user_id].get('interests', [])

        if interest in user_interests:
            user_interests.remove(interest)
        else:
            if len(user_interests) < 5:
                user_interests.append(interest)
            else:
                await query.answer("❌ Maximum 5 interests allowed!")
                return

        user_profiles[user_id]['interests'] = user_interests

        # Refresh the interests menu
        await self.show_interests_menu(query, context)
        await query.answer(
            f"{'✅ Added' if interest in user_interests else '❌ Removed'}: {interest}"
        )

    async def show_preferences_menu(self, query, context):
        """Show user preferences menu"""
        user_id = query.from_user.id
        settings = user_profiles[user_id].get('settings', {})

        text = """
⚙️ **Chat Preferences**

Customize your anonymous chat experience:
        """

        keyboard = [
            [
                InlineKeyboardButton(
                    f"🌍 Language: {user_profiles[user_id].get('preferred_language', 'Not Set')}",
                    callback_data="set_language")
            ],
            [
                InlineKeyboardButton(
                    f"🔄 Auto-Translate: {'ON' if settings.get('auto_translate') else 'OFF'}",
                    callback_data="toggle_translate")
            ],
            [
                InlineKeyboardButton(
                    f"🛡️ Content Filter: {'ON' if settings.get('filter_inappropriate') else 'OFF'}",
                    callback_data="toggle_filter")
            ],
            [
                InlineKeyboardButton(
                    f"⌨️ Typing Indicator: {'ON' if settings.get('show_typing') else 'OFF'}",
                    callback_data="toggle_typing")
            ],
            [
                InlineKeyboardButton(
                    f"🎵 Voice Messages: {'ON' if settings.get('allow_voice_messages') else 'OFF'}",
                    callback_data="toggle_voice")
            ], [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      reply_markup=reply_markup,
                                      parse_mode='Markdown')

    async def show_games_menu(self, query, context):
        """Show interactive games menu"""
        text = """
🎮 **Chat Games & Activities**

Make your conversations more fun and engaging!
        """

        keyboard = [
            [
                InlineKeyboardButton("🎯 20 Questions",
                                     callback_data="game_20questions"),
                InlineKeyboardButton("🎲 Truth or Dare",
                                     callback_data="game_truthdare")
            ],
            [
                InlineKeyboardButton("🧩 Word Chain",
                                     callback_data="game_wordchain"),
                InlineKeyboardButton("🎨 Drawing Game",
                                     callback_data="game_drawing")
            ],
            [
                InlineKeyboardButton("🎭 Role Play",
                                     callback_data="game_roleplay"),
                InlineKeyboardButton("💭 Story Building",
                                     callback_data="game_story")
            ],
            [
                InlineKeyboardButton("🎪 Random Activities",
                                     callback_data="game_random"),
                InlineKeyboardButton("💡 Conversation Starters",
                                     callback_data="conversation_starters")
            ], [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text,
                                      reply_markup=reply_markup,
                                      parse_mode='Markdown')

    async def show_user_stats(self, query, context):
        """Show detailed user statistics"""
        user_id = query.from_user.id
        profile = user_profiles[user_id]

        # Calculate advanced stats
        join_days = (datetime.now() - profile['join_date']).days
        avg_chats_per_day = profile['total_chats'] / max(join_days, 1)

        text = f"""
📊 **Your Chat Statistics**

👤 **Profile:**
• Username: {profile['username']}
• Member since: {profile['join_date'].strftime('%B %d, %Y')}
• Status: {'🌟 VIP Member' if profile['is_vip'] else '👤 Regular User'}

📈 **Activity:**
• Total chats: {profile['total
