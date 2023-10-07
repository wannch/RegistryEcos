import json

with open('transformers.json', 'r') as f:
    meta_dict = json.load(f)

print(meta_dict.keys())

print(meta_dict['releases'].keys())
print('*' * 100)
print(meta_dict['urls'])

