import os
model_dl_dir = "model"
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
schema_file=os.path.join(CURRENT_DIR, model_dl_dir, "schema.json")
eradication_path=os.path.join(CURRENT_DIR, model_dl_dir, "Eradication")
assets_input_dir="Assets"
reporters=model_dl_dir
sif=os.path.join(CURRENT_DIR, "dtk_run_rocky_py39_pymysql_stage.id")
sif_filename="dtk_run_rocky_py39_mysql.sif"
ep4=os.path.join(CURRENT_DIR, "EP4")
REFERENCE_DATA_DIR= os.path.join(CURRENT_DIR, 'reference')
