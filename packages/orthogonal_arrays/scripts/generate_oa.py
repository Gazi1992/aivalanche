from utils import generate_oa_by_elimination, fetch_oa_from_file, generate_oa_by_addition, generate_oa_by_addition_parallel
import os

# #%% Test single OA by elimination
# nr_factors = 10
# levels = 3
# strength = 3
# nr_restarts = 10
# file_path = os.path.join(f'../results/oa_{nr_factors}_{levels}_{strength}.json')
# file_path = None
# oa = generate_oa_by_addition(nr_factors, levels, strength, nr_restarts, file_path, False)

# #%% Test single OA by addition
# nr_factors = 4
# levels = 3
# strength = 3
# nr_restarts = 5
# file_path = os.path.join(f'../results/oa_{nr_factors}_{levels}_{strength}.json')
# file_path = None
# oa = generate_oa_by_elimination(nr_factors, levels, strength, nr_restarts, file_path, True)

# #%% Test reading OA from file
# nr_factors = 4
# levels = 3
# strength = 3
# file_path = os.path.join(f'../results/oa_{nr_factors}_{levels}_{strength}.json')
# oa = fetch_oa_from_file(file_path)

# #%% Build many OA-s by elimination
# factors = [4, 5, 6, 7, 8, 9, 10]
# levels = [2, 3, 4, 5]
# strengths = [2, 3, 4]
# nr_restarts = 5
# for s in strengths:
#     for l in levels:
#         for f in factors:
#             try:
#                 file_path = os.path.join(f'../results/oa_{f}_{l}_{s}.json')
#                 oa = generate_oa_by_elimination(f, l, s, nr_restarts, file_path, False)
#             except Exception as e:
#                 print(e)
#                 pass           
            
#%% Build many OA-s by addition
factors = range(26) #[4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
levels = [2, 3, 4, 5]
strengths = [2, 3, 4, 5]
nr_restarts = 10
for s in strengths:
    for l in levels:
        for f in factors:
            try:
                file_path = os.path.join(f'../results/oa_{f}_{l}_{s}.json')
                oa = generate_oa_by_addition_parallel(f, l, s, nr_restarts, file_path, False)
            except Exception as e:
                print(e)
                pass           
