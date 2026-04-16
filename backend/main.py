import os
import sys
import asyncio
import subprocess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import glob

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="LongTailLib API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskManager:
    def __init__(self):
        self.current_process = None
        self.active_websockets = []
        self.message_queue = asyncio.Queue()
        self.broadcast_task = None
        
    def start_broadcasting(self):
        if self.broadcast_task is None:
            self.broadcast_task = asyncio.create_task(self._broadcast_loop())

    async def _broadcast_loop(self):
        while True:
            msg = await self.message_queue.get()
            dead_sockets = []
            for ws in self.active_websockets:
                try:
                    await ws.send_text(msg)
                except Exception:
                    dead_sockets.append(ws)
            for ws in dead_sockets:
                self.active_websockets.remove(ws)

    def log(self, message: str):
        if not message.endswith("\n"):
            message += "\n"
        self.message_queue.put_nowait(message)

    async def run_command_async(self, cmd, cwd=None):
        if self.current_process is not None and self.current_process.returncode is None:
            raise HTTPException(status_code=400, detail="Task already running")

        self.log(f">>> 开始执行: {' '.join(cmd)}")
        
        env = os.environ.copy()
        env['PYTHONUNBUFFERED'] = '1'

        try:
            loop = asyncio.get_running_loop()
            self.current_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=cwd,
                env=env
            )
            
            def read_stdout(proc, log_func):
                try:
                    for line in iter(proc.stdout.readline, b''):
                        decoded_line = line.decode('utf-8', errors='replace')
                        loop.call_soon_threadsafe(log_func, decoded_line)
                finally:
                    proc.stdout.close()
            
            import threading
            reader_thread = threading.Thread(target=read_stdout, args=(self.current_process, self.log))
            reader_thread.daemon = True
            reader_thread.start()
            
            def wait_proc():
                return self.current_process.wait()
                
            returncode = await loop.run_in_executor(None, wait_proc)
            
            if returncode == 0:
                self.log(">>> 执行成功完成。")
            elif returncode < 0:
                self.log(">>> 执行被手动终止。")
            else:
                self.log(f">>> 执行出错，返回码: {returncode}")
                
        except Exception as e:
            import traceback
            err_msg = str(e) if str(e) else repr(e)
            self.log(f">>> 发生系统错误: {err_msg}\n{traceback.format_exc()}")
        finally:
            self.current_process = None

    def stop_command(self):
        if self.current_process is not None and self.current_process.returncode is None:
            self.current_process.terminate()
            self.log(">>> 正在发送终止信号...\n")
            return True
        return False

task_manager = TaskManager()

@app.on_event("startup")
async def startup_event():
    task_manager.start_broadcasting()

# Models
class DatasetGenerateReq(BaseModel):
    ds_name: str
    ds_niid: str
    ds_balance: str
    ds_partition: str
    ds_longtail: str
    ds_type: str
    ds_if: str
    ds_alpha: str
    ds_clients: str

class TrainStartReq(BaseModel):
    dataset: str
    algo: str
    model: str
    gr: str
    did: str
    seed: str

class CompareReq(BaseModel):
    dataset: str

@app.post("/api/dataset/generate")
async def generate_dataset(req: DatasetGenerateReq):
    script = os.path.join(BASE_DIR, "dataset", f"generate_{req.ds_name}.py")
    if not os.path.exists(script):
        raise HTTPException(status_code=404, detail=f"Script not found: {script}")

    cmd = [
        sys.executable,
        script,
        req.ds_niid,
        req.ds_balance,
        req.ds_partition,
    ]
    if req.ds_longtail == "longtail":
        cmd.extend(["longtail", req.ds_type, req.ds_if])
    cmd.extend([req.ds_alpha, req.ds_clients])
    
    if task_manager.current_process is not None and task_manager.current_process.returncode is None:
        raise HTTPException(status_code=400, detail="Task already running")

    asyncio.create_task(task_manager.run_command_async(cmd, cwd=os.path.join(BASE_DIR, "dataset")))
    return {"message": "Started", "cmd": cmd}

@app.get("/api/dataset/list")
async def list_datasets():
    ds_path = os.path.join(BASE_DIR, "dataset")
    if not os.path.exists(ds_path):
        return {"datasets": []}
    dirs = [d for d in os.listdir(ds_path) if os.path.isdir(os.path.join(ds_path, d)) and (d.startswith("Cifar") or d.startswith("MNIST"))]
    return {"datasets": sorted(dirs)}

@app.post("/api/train/start")
async def start_training(req: TrainStartReq):
    script_path = os.path.join(BASE_DIR, "system", "main.py")
    if not os.path.exists(script_path):
        raise HTTPException(status_code=404, detail="system/main.py not found")
        
    cmd = [
        sys.executable,
        "main.py",
        "-data", req.dataset,
        "-algo", req.algo,
        "-m", req.model,
        "-gr", req.gr,
        "-did", req.did,
        "-seed", req.seed
    ]
    
    cwd_path = os.path.join(BASE_DIR, "system")
    if task_manager.current_process is not None and task_manager.current_process.returncode is None:
        raise HTTPException(status_code=400, detail="Task already running")

    asyncio.create_task(task_manager.run_command_async(cmd, cwd=cwd_path))
    return {"message": "Training started"}

@app.post("/api/task/stop")
async def stop_task():
    success = task_manager.stop_command()
    if success:
        return {"message": "Task stopped"}
    else:
        return {"message": "No running task"}

@app.get("/api/results/list")
async def list_results():
    results_dir = os.path.join(BASE_DIR, "results")
    if not os.path.exists(results_dir):
        return {"datasets": []}
    
    datasets = set()
    for d in os.listdir(results_dir):
        if os.path.isdir(os.path.join(results_dir, d)):
            parts = d.rsplit('_', 3)
            if len(parts) >= 3:
                ds_name = parts[0]
                datasets.add(ds_name)
                
    return {"datasets": sorted(list(datasets))}

@app.post("/api/results/compare")
async def compare_results(req: CompareReq):
    ds_target = req.dataset
    results_dir = os.path.join(BASE_DIR, "results")
    
    try:
        import h5py
        import matplotlib.pyplot as plt
        import io
        import base64
    except ImportError:
        raise HTTPException(status_code=500, detail="Missing h5py or matplotlib")

    algo_files = {}
    if not os.path.exists(results_dir):
         raise HTTPException(status_code=404, detail="No results folder found")

    for d in os.listdir(results_dir):
        dir_path = os.path.join(results_dir, d)
        if os.path.isdir(dir_path) and d.startswith(ds_target + "_"):
            parts = d.rsplit('_', 3)
            if len(parts) >= 3 and parts[0] == ds_target:
                algo = parts[-3]
                h5_path = os.path.join(dir_path, f"{d}.h5")
                if os.path.exists(h5_path):
                    if algo not in algo_files or d > algo_files[algo][0]:
                        algo_files[algo] = (d, h5_path)
    
    if not algo_files:
        raise HTTPException(status_code=404, detail="No valid experimental results found")
        
    table_lines = []
    table_lines.append(f"\n====================== 实验结果最终指标对比 ======================")
    table_lines.append(f"数据集: {ds_target}")
    table_lines.append(f"{'算法 (Algorithm)':<15} | {'最佳整体准确率':<15} | {'最佳尾部准确率':<15} | {'最小类间方差':<15}")
    table_lines.append("-" * 75)
    
    for algo, (d, h5_path) in algo_files.items():
        best_g, best_t, min_v = "-", "-", "-"
        with h5py.File(h5_path, 'r') as hf:
            if 'rs_global_acc' in hf and len(hf['rs_global_acc']) > 0:
                best_g = f"{max(hf['rs_global_acc'][:]):.4f}"
            if 'rs_tail_acc' in hf and len(hf['rs_tail_acc']) > 0:
                best_t = f"{max(hf['rs_tail_acc'][:]):.4f}"
            if 'rs_acc_var' in hf and len(hf['rs_acc_var']) > 0:
                min_v = f"{min(hf['rs_acc_var'][:]):.4f}"
        table_lines.append(f"{algo:<20} | {best_g:<22} | {best_t:<22} | {min_v:<20}")
    table_lines.append("==================================================================\n")
    
    for line in table_lines:
        task_manager.log(line)

    plt.figure(figsize=(18, 5))
    
    plt.subplot(1, 3, 1)
    for algo, (d, h5_path) in algo_files.items():
        with h5py.File(h5_path, 'r') as hf:
            if 'rs_global_acc' in hf:
                data = hf['rs_global_acc'][:]
                plt.plot(data, label=algo, linewidth=2)
    plt.title('Global Test Accuracy')
    plt.xlabel('Round')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 2)
    for algo, (d, h5_path) in algo_files.items():
        with h5py.File(h5_path, 'r') as hf:
            if 'rs_tail_acc' in hf:
                data = hf['rs_tail_acc'][:]
                plt.plot(data, label=algo, linewidth=2)
    plt.title('Tail Class Average Accuracy')
    plt.xlabel('Round')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 3, 3)
    for algo, (d, h5_path) in algo_files.items():
        with h5py.File(h5_path, 'r') as hf:
            if 'rs_acc_var' in hf:
                data = hf['rs_acc_var'][:]
                plt.plot(data, label=algo, linewidth=2)
    plt.title('Inter-class Accuracy Variance')
    plt.xlabel('Round')
    plt.ylabel('Variance')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=300)
    plt.close()
    buf.seek(0)
    
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    
    save_path = os.path.join(results_dir, f"Comparison_{ds_target}.png")
    try:
        with open(save_path, "wb") as f:
            f.write(base64.b64decode(img_b64))
        task_manager.log(f">>> 对比图已生成: {save_path}")
    except Exception as e:
         pass
         
    return {"message": "Success", "image_base64": f"data:image/png;base64,{img_b64}"}

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await websocket.accept()
    task_manager.active_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in task_manager.active_websockets:
            task_manager.active_websockets.remove(websocket)
