from fastapi import APIRouter, Request
import httpx
import os
from api.routers.meals import log_meal_internal  # Use existing meal logging

# NEW router - completely separate from existing webhook
router = APIRouter(prefix="/telegram-bot", tags=["Telegram Bot"])

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@router.post("/webhook")
async def telegram_bot_webhook(request: Request):
    """Handle ONLY Telegram bot messages - separate from existing webhook"""
    
    try:
        data = await request.json()
        
        # Only process if it's a message
        if "message" not in data:
            return {"ok": True}
        
        message = data["message"]
        
        # Process the message using the updated handler
        await handle_message(message)
        
        return {"ok": True}
        
    except Exception as e:
        print(f"Telegram webhook error: {e}")
        return {"ok": True}

async def handle_telegram_log_command(chat_id: int, text: str, user_info: dict):
    """Process /log command from Telegram"""
    
    try:
        # Parse: "/log user_1 lunch: rice, dal, vegetables"
        if ":" not in text:
            await send_format_help_message(chat_id)
            return
        
        # Extract command parts
        parts = text.split(":", 1)
        command_part = parts[0].replace("/log", "").strip()
        items_part = parts[1].strip()
        
        # Check if user_id and meal_type are provided
        command_words = command_part.split()
        
        if len(command_words) != 2:
            await send_format_help_message(chat_id)
            return
        
        user_id = command_words[0]
        meal_type = command_words[1].lower()
        
        # Validate meal type
        valid_meal_types = ["breakfast", "lunch", "dinner", "snack"]
        if meal_type not in valid_meal_types:
            await send_telegram_message(chat_id, 
                f"❌ Invalid meal type '{meal_type}'\n\n"
                f"Valid meal types: {', '.join(valid_meal_types)}\n\n"
                "Use /help for correct format")
            return
        
        food_items = [item.strip() for item in items_part.split(",")]
        
        # Validate food items are not empty
        if not food_items or all(not item.strip() for item in food_items):
            await send_telegram_message(chat_id,
                "❌ No food items provided\n\n"
                "Example: /log user_1 lunch: rice, dal, vegetables\n\n"
                "Use /help for correct format")
            return
        
        # Use your EXISTING meal logging function
        result = await log_meal_internal(user_id, meal_type, food_items)
        
        if result.get("success"):
            nutrition = result.get("nutrition", {})
            response = f"""✅ Meal logged successfully for {user_id}!

🍽️ Meal: {meal_type}
📊 Nutrition Added:
🔥 Calories: {nutrition.get('calories', 0)} kcal
🥩 Protein: {nutrition.get('protein', 0)}g
🌾 Carbs: {nutrition.get('carbs', 0)}g
🌿 Fiber: {nutrition.get('fiber', 0)}g"""
        else:
            error_type = result.get("error_type", "unknown")
            error_msg = result.get("error", "Unknown error")
            
            if error_type == "user_not_found":
                response = await generate_user_not_found_message(user_id, meal_type, food_items)
            elif error_type == "unknown_foods":
                response = await generate_unknown_foods_message(error_msg)
            else:
                response = f"❌ Error: {error_msg}\n\nUse /help for correct format"
        
        await send_telegram_message(chat_id, response)
        
    except Exception as e:
        await send_telegram_message(chat_id, 
            f"❌ Error processing meal: {str(e)}\n\nUse /help for correct format")

async def generate_user_not_found_message(user_id: str, meal_type: str, food_items: list):
    """Generate detailed message when user is not found"""
    
    food_items_str = ", ".join(food_items)
    
    message = f"""❌ User '{user_id}' not found!

🆕 **To create this user and log the meal, use this format:**

```
POST /api/v1/users/register
Content-Type: application/json

{{
  "name": "User Name",
  "age": 25,
  "weight": 70.0,
  "height": 175.0,
  "gender": "male",
  "goal": "maintain",
  "userId": "{user_id}"
}}
```

📋 **Then your meal will be logged:**
- User: {user_id}
- Meal: {meal_type}
- Items: {food_items_str}

💡 **Quick Options:**
• Register user via web app: https://meal-metrics-api.onrender.com/frontend/index.html#register
• Use API documentation: https://meal-metrics-api.onrender.com/docs
• Contact admin to create user '{user_id}'

ℹ️ Use /help to see command format"""

    return message

async def generate_unknown_foods_message(error_msg: str):
    """Generate message for unknown food items"""
    
    message = f"""❌ {error_msg}

🍽️ **Available foods include:**
• Grains: Rice, Basmati Rice, Roti, Chapati, Naan
• Proteins: Dal, Toor Dal, Moong Dal, Chicken Curry, Paneer
• Vegetables: Cucumber, Tomato, Onion, Potato, Carrot
• Fruits: Apple, Banana, Orange

📋 **Get full food list:**
• Web: https://meal-metrics-api.onrender.com/docs
• API: GET /api/v1/nutrition/foods

ℹ️ Use /help to see command format"""

    return message

async def send_format_help_message(chat_id: int):
    """Send message about correct format"""
    
    message = """❌ Incorrect format!

✅ **Correct format:**
`/log [user_id] [meal_type]: [food_items]`

📝 **Examples:**
• `/log user_1 breakfast: oats, banana, milk`
• `/log john_doe lunch: rice, dal, vegetables`
• `/log admin dinner: chicken curry, roti, salad`

📋 **Required:**
• `user_id`: Must be registered user
• `meal_type`: breakfast, lunch, dinner, or snack
• `food_items`: Comma-separated list

ℹ️ Use /help for more details"""

    await send_telegram_message(chat_id, message, parse_mode="Markdown")

async def handle_message(message: dict):
    """Process incoming Telegram message"""
    
    chat_id = message["chat"]["id"]
    text = message.get("text", "")
    user_info = message["from"]
    
    if text.startswith("/log"):
        await handle_telegram_log_command(chat_id, text, user_info)
    elif text.startswith("/help") or text == "/start":
        await send_help_message(chat_id)
    else:
        # Send help message for any other text
        await send_help_message(chat_id)

async def send_help_message(chat_id: int):
    """Send help message with command examples"""
    
    message = """🤖 **BMR Meal Tracker Bot Commands**

📝 **Log meals for existing users:**
`/log user_1 breakfast: oats, banana, milk`
`/log user_2 lunch: rice, dal, vegetables`
`/log admin dinner: chicken, roti, salad`

📋 **Required Format:**
`/log [user_id] [meal_type]: [food_items]`

🍽️ **Meal Types:**
breakfast, lunch, dinner, snack

💡 **Tips:**
• Use exact user_id from your system
• Separate food items with commas
• Bot will provide detailed help if user doesn't exist
• Bot will show available foods for unknown items

❓ **Need help?** Send /help anytime"""

    await send_telegram_message(chat_id, message, parse_mode="Markdown")

async def send_telegram_message(chat_id: int, text: str, parse_mode: str = None):
    """Send message back to Telegram user"""
    
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN not set")
        return
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    
    if parse_mode:
        payload["parse_mode"] = parse_mode
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"Error sending Telegram message: {e}")
