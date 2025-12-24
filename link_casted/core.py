from openpyxl import load_workbook
import bpy
import os


def find_dir_ep(blend_path):
    blend_path = bpy.data.filepath
    ep_dir = blend_path
    for i in range(6):
        ep_dir = os.path.dirname(ep_dir)
        # print("ep_dir", ep_dir)
    return ep_dir

def find_xlsx(ep_dir):
    ep = os.path.basename(find_dir_ep(ep_dir))
    xlsx_path = os.path.join(ep_dir,f"EP{ep}_Material" ,f'MM_{ep}_VB_01_shotlist.xlsx')
    # print("xlsx_path",xlsx_path)
    return xlsx_path


def match_shot():
    blend_path = bpy.data.filepath
    filename = find_xlsx(find_dir_ep(blend_path))
    workbook = load_workbook(filename=filename, data_only=True)
    
    blend_name = bpy.path.basename(blend_path)
    ep = blend_name.split('_')[1]
    #Check first column to find the good asset_txt = row[j].value and not set it manually
    for j, col in enumerate(workbook[f'MM_{ep}_VB_01'].iter_cols()):
        if col[0].value != 'assetListAnimation' : continue 
        # print(col[0].value )
        for i, row in enumerate(workbook[f'MM_{ep}_VB_01'].iter_rows()):
            num = row[2].value
            asset_txt = row[j].value
            if not isinstance(num, (int, float)):continue
            if blend_name.split('_')[3] == f"{int(num):04d}":
                assets = [p.strip() for p in asset_txt.split('-') if p.strip()]
                # print(f"yes chef {assets} correspond a blendfile {int(num):04d} au row {i+1}")
                return assets, num



def find_file(match_shot):
    candidates = []
    assets, num = match_shot
    # print(assets, "num :", num)
    base_chars = r"R:\melodyandmomon\Assets\Characters"
    base_props = r"R:\melodyandmomon\Assets\Props"
    base_sets = r"R:\melodyandmomon\Assets\Sets"
    base_set_items = r"R:\melodyandmomon\Assets\Set_Items"
    final_rd_path = "Final\Render"
    final_lod_path = "Final\Lo"
    for asset in assets:
        if asset.split('_')[1] == 'CHR':
            candidate = os.path.join(base_chars, asset, final_rd_path, f'{asset}.blend')
            print(os.path.join(base_chars, asset, final_rd_path, f'{asset}.blend'))
        elif asset.split('_')[1] == 'PRP':
            candidate = os.path.join(base_props, asset, final_rd_path, f'{asset}.blend')
        elif asset.split('_')[1] == 'ITM':
            candidate = os.path.join(base_set_items, asset, final_rd_path, f'{asset}.blend')
        elif asset.split('_')[1] == 'SET':
            candidate = os.path.join(base_sets, asset, final_lod_path, f'{asset}.blend')
        else:
            continue
        if os.path.exists(candidate):
            candidates.append(candidate)
            # print("append")
    return candidates