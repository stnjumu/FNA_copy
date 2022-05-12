# 查看checkpoint dict的保存形式
import torch

filename = './seed_mbv2.pt'
checkpoint = torch.load(filename, map_location='cpu')
print(checkpoint)

# for k in model_dict.keys():
#         if k in seed_dict:
#             depth_mapped_dict[k] = seed_dict[k]
#         elif 'blocks.1' in k:
#             seed_key = re.sub('blocks.1', 'blocks.1.layers.0', k)
#             if 'tracked' in seed_key and seed_key not in seed_dict:
#                 continue
#             depth_mapped_dict[k] = seed_dict[seed_key]
#         elif 'blocks.' in k and 'layers.' in k:
#             block_id = int(k.split('.')[1])
#             layer_id = int(k.split('.')[3])
#             seed_layer_id = seed_num_layers[block_id]-1
#             seed_key = re.sub('layers.'+str(layer_id), 
#                             'layers.'+str(min(seed_layer_id, layer_id)), 
#                             k[:18]) + k[29:]
#             if 'tracked' in seed_key and seed_key not in seed_dict:
#                 continue
#             depth_mapped_dict[k] = seed_dict[seed_key]