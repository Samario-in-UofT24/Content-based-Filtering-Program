import json
import ast

# Load the datas
with open('australian_users_items.json', 'r', encoding='utf-8') as f_items:
    items_data = [ast.literal_eval(line) for line in f_items if line.strip()]

with open('australian_user_reviews.json', 'r', encoding='utf-8') as f_reviews:
    reviews_data = [ast.literal_eval(line) for line in f_reviews if line.strip()]

# Construct a dict to go through the reviews and recommend(bool)
user_reviews_map = {}
for entry in reviews_data:
    user_id = entry['user_id']
    user_reviews_map[user_id] = {review['item_id']: {
        'review': review['review'],
        'recommend': review['recommend']
    } for review in entry.get('reviews', [])}

# New data list
filtered_data = []

for entry in items_data:
    user_id = entry['user_id']
    for item in entry.get('items', []):
        item_entry = {
            'user_id': user_id,
            'item_id': item['item_id'],
            'item_name': item['item_name'],
            'playtime_forever': item['playtime_forever']
        }

        # If there is a review, then add review and recommend(bool)
        if user_id in user_reviews_map and item['item_id'] in user_reviews_map[user_id]:
            item_entry.update(user_reviews_map[user_id][item['item_id']])

        filtered_data.append(item_entry)

# Give out the new files
with open('filtered_data.json', 'w', encoding='utf-8') as f_out:
    for entry in filtered_data:
        f_out.write(json.dumps(entry) + '\n')

print(f'Finished, imports {len(filtered_data)} of data filtered_data.json')
