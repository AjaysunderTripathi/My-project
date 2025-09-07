from collections import defaultdict

# In-memory context store (replace with DB for production)
user_contexts = defaultdict(list)

def update_context(user_id, user_input):
    ctx = user_contexts[user_id]
    ctx.append(user_input)
    user_contexts[user_id] = ctx[-5:]  # Keep last 5 turns
    return user_contexts[user_id]

def get_context(user_id):
    return user_contexts[user_id]
