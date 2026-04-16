import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
import queue


# Set unbuffered I/O for Python to ensure stdout is flushed immediately
os.environ['PYTHONUNBUFFERED'] = '1'


class LongTailLibGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("LongTailLib 联邦长尾学习评测平台控制台")
        self.root.geometry("900x700")

        # 任务队列和状态
        self.log_queue = queue.Queue()
        self.current_process = None
        self._check_log_queue()

        # 样式设置
        style = ttk.Style()
        style.theme_use('clam')

        # 主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 选项卡控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # --- 选项卡 1: 数据集生成 ---
        self.tab_dataset = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dataset, text=" 1. 数据集生成 (Dataset) ")
        self._init_dataset_tab()

        # --- 选项卡 2: 算法训练 ---
        self.tab_train = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_train, text=" 2. 算法训练 (Training) ")
        self._init_train_tab()

        # --- 选项卡 3: 结果对比 ---
        self.tab_compare = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_compare, text=" 3. 结果对比 (Comparison) ")
        self._init_compare_tab()

        # --- 底部: 日志输出 ---
        log_labelframe = ttk.LabelFrame(main_frame, text="控制台日志 (Console Log)")
        log_labelframe.pack(fill=tk.BOTH, expand=True, pady=10)

        log_btn_frame = ttk.Frame(log_labelframe)
        log_btn_frame.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(log_btn_frame, text="清空日志 (Clear)", command=self._clear_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(log_btn_frame, text="停止当前任务 (Stop Task)", command=self._stop_command).pack(side=tk.LEFT, padx=5)

        self.log_text = scrolledtext.ScrolledText(log_labelframe, height=15, state='disabled', bg="#1e1e1e",
                                                  fg="#00ff00", font=("Consolas", 10))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _check_log_queue(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.log_text.config(state='normal')
            self.log_text.insert(tk.END, message)
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
        self.root.after(100, self._check_log_queue)

    def _clear_log(self):
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    def _stop_command(self):
        if self.current_process is not None and self.current_process.poll() is None:
            self.current_process.terminate()
            self._log(">>> 正在发送终止信号...\n")
        else:
            messagebox.showinfo("提示", "当前没有正在运行的任务。")

    def _log(self, message):
        if not message.endswith('\n'):
            message += '\n'
        self.log_queue.put(message)

    def _run_command(self, cmd, cwd=None):
        """在独立线程中运行命令，防止界面卡死 """
        if self.current_process is not None and self.current_process.poll() is None:
            messagebox.showwarning("警告", "当前有任务正在运行，请先停止或等待其完成。")
            return

        def target():
            self._log(f">>> 开始执行: {' '.join(cmd)}")
            try:
                # 增加环境变量以确保子进程的标准输出不被缓存
                env = os.environ.copy()
                env['PYTHONUNBUFFERED'] = '1'

                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    cwd=cwd,
                    bufsize=1,
                    text=True,  # 保持文本模式
                    encoding='utf-8',  # 优先尝试 UTF-8
                    errors='replace',  # 遇到乱码直接替换
                    env=env
                )

                # 逐行读取输出
                for line in self.current_process.stdout:
                    self._log(line)

                self.current_process.wait()
                if self.current_process.returncode == 0:
                    self._log(">>> 执行成功完成。")
                    # 如果是生成数据集，刷新训练页面的数据集列表
                    if "generate" in cmd[1]:
                        self.root.after(0, self._refresh_dataset_list)
                else:
                    if self.current_process.returncode < 0:
                        self._log(">>> 执行被手动终止。")
                    else:
                        self._log(f">>> 执行出错，返回码: {self.current_process.returncode}")
            except Exception as e:
                self._log(f">>> 发生系统错误: {str(e)}")
            finally:
                self.current_process = None

        threading.Thread(target=target, daemon=True).start()

    # ================= 数据集生成界面 =================
    def _init_dataset_tab(self):
        frame = ttk.Frame(self.tab_dataset, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        grid_opts = {'padx': 5, 'pady': 10, 'sticky': 'w'}

        # 0. 目标数据集
        ttk.Label(frame, text="目标数据集 (Target):").grid(row=0, column=0, **grid_opts)
        self.ds_name = tk.StringVar(value="Cifar10")
        ttk.Combobox(frame, textvariable=self.ds_name, values=["Cifar10", "Cifar100", "MNIST"], state="readonly", width=12).grid(row=0, column=1, **grid_opts)

        # 1. IID 设置
        ttk.Label(frame, text="分布类型 (Distribution):").grid(row=0, column=2, **grid_opts)
        self.ds_niid = tk.StringVar(value="noniid")
        ttk.Combobox(frame, textvariable=self.ds_niid, values=["noniid", "iid"], state="readonly", width=12).grid(row=0, column=3, **grid_opts)

        # 2. 数量平衡
        ttk.Label(frame, text="数据量平衡 (Balance):").grid(row=1, column=0, **grid_opts)
        self.ds_balance = tk.StringVar(value="-")  # 对应 '-' (不平衡) 或 'balance'
        ttk.Combobox(frame, textvariable=self.ds_balance, values=["-", "balance"], state="readonly", width=12).grid(row=1, column=1, **grid_opts)

        # 3. 划分方式
        ttk.Label(frame, text="划分策略 (Partition):").grid(row=1, column=2, **grid_opts)
        self.ds_partition = tk.StringVar(value="dir")
        ttk.Combobox(frame, textvariable=self.ds_partition, values=["dir", "pat", "exdir"], state="readonly", width=12).grid(row=1, column=3, **grid_opts)

        # 4. 长尾设置
        ttk.Label(frame, text="启用长尾 (Longtail):").grid(row=2, column=0, **grid_opts)
        self.ds_longtail = tk.StringVar(value="longtail")
        ttk.Checkbutton(frame, text="启用", variable=self.ds_longtail, onvalue="longtail", offvalue="normal").grid(row=2, column=1, **grid_opts)

        # 5. 长尾类型
        ttk.Label(frame, text="长尾类型 (Type):").grid(row=2, column=2, **grid_opts)
        self.ds_type = tk.StringVar(value="global")
        ttk.Combobox(frame, textvariable=self.ds_type, values=["global", "local"], state="readonly", width=12).grid(row=2, column=3, **grid_opts)

        # 6. 不平衡因子 IF
        ttk.Label(frame, text="不平衡因子 (IF):").grid(row=3, column=0, **grid_opts)
        self.ds_if = tk.StringVar(value="50")
        ttk.Entry(frame, textvariable=self.ds_if, width=15).grid(row=3, column=1, **grid_opts)

        # 7. Alpha
        ttk.Label(frame, text="Dirichlet Alpha:").grid(row=3, column=2, **grid_opts)
        self.ds_alpha = tk.StringVar(value="0.5")
        ttk.Entry(frame, textvariable=self.ds_alpha, width=15).grid(row=3, column=3, **grid_opts)

        # 8. 客户端数量
        ttk.Label(frame, text="客户端数量 (Num Clients):").grid(row=4, column=0, **grid_opts)
        self.ds_clients = tk.StringVar(value="20")
        ttk.Entry(frame, textvariable=self.ds_clients, width=15).grid(row=4, column=1, **grid_opts)

        # 说明
        info_lbl = ttk.Label(frame,
                             text="说明: 将调用 dataset/generate_*.py (若无数据请先手动下载对应数据集到rawdata)",
                             foreground="gray")
        info_lbl.grid(row=5, column=0, columnspan=4, pady=20)

        # 生成按钮
        btn = ttk.Button(frame, text="生成数据集 (Generate Dataset)", command=self._on_generate_click)
        btn.grid(row=6, column=0, columnspan=4, ipadx=20, ipady=5)

    def _on_generate_click(self):
        script = os.path.join("dataset", f"generate_{self.ds_name.get()}.py")
        if not os.path.exists(script):
            messagebox.showerror("错误", f"找不到文件: {script}\n请确保 gui.py 在项目根目录运行。")
            return

        cmd = [
            sys.executable,
            script,
            self.ds_niid.get(),  # 1: noniid
            self.ds_balance.get(),  # 2: balance / -
            self.ds_partition.get()  # 3: dir
        ]

        if self.ds_longtail.get() == "longtail":
            cmd.append("longtail")  # 4
            cmd.append(self.ds_type.get())  # 5: global
            cmd.append(self.ds_if.get())  # 6: IF
        else:
            pass

        cmd.append(self.ds_alpha.get())  # 7
        cmd.append(self.ds_clients.get())  # 8

        self._run_command(cmd)

    # ================= 算法训练界面 =================
    def _init_train_tab(self):
        frame = ttk.Frame(self.tab_train, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        grid_opts = {'padx': 5, 'pady': 10, 'sticky': 'w'}

        # 1. 选择数据集 (自动扫描)
        ttk.Label(frame, text="选择数据集 (Dataset):").grid(row=0, column=0, **grid_opts)
        self.tr_dataset = tk.StringVar()
        self.combo_dataset = ttk.Combobox(frame, textvariable=self.tr_dataset, width=40)
        self.combo_dataset.grid(row=0, column=1, columnspan=3, **grid_opts)

        # 刷新按钮
        ttk.Button(frame, text="刷新列表", command=self._refresh_dataset_list).grid(row=0, column=4, padx=5)

        # 2. 算法选择
        ttk.Label(frame, text="算法 (Algorithm):").grid(row=1, column=0, **grid_opts)
        self.tr_algo = tk.StringVar(value="CReFF")
        algos = ["CReFF", "CLIP2FL", "CCVR", "RUCR", "FedETF", "FedLoGe", "FedNH", "FedIC", "FedGraB", "FedAvg",
                 "FedProx"]
        ttk.Combobox(frame, textvariable=self.tr_algo, values=algos, state="readonly", width=15).grid(row=1, column=1,
                                                                                                      **grid_opts)

        # 3. 模型选择
        ttk.Label(frame, text="模型 (Model):").grid(row=1, column=2, **grid_opts)
        self.tr_model = tk.StringVar(value="ResNet8")
        models = ["ResNet8", "ResNet18", "ResNet20", "ResNet34", "CNN", "MobileNet"]
        ttk.Combobox(frame, textvariable=self.tr_model, values=models, width=15).grid(row=1, column=3, **grid_opts)

        # 4. 全局轮数
        ttk.Label(frame, text="全局轮数 (Global Rounds):").grid(row=2, column=0, **grid_opts)
        self.tr_gr = tk.StringVar(value="200")
        ttk.Entry(frame, textvariable=self.tr_gr, width=10).grid(row=2, column=1, **grid_opts)

        # 5. GPU ID
        ttk.Label(frame, text="GPU 设备 ID (-did):").grid(row=2, column=2, **grid_opts)
        self.tr_did = tk.StringVar(value="0")
        ttk.Entry(frame, textvariable=self.tr_did, width=10).grid(row=2, column=3, **grid_opts)

        # 6. 随机种子 Random Seed
        ttk.Label(frame, text="随机种子 (Random Seed):").grid(row=3, column=0, **grid_opts)
        self.tr_seed = tk.StringVar(value="7")
        ttk.Entry(frame, textvariable=self.tr_seed, width=10).grid(row=3, column=1, **grid_opts)

        # 说明
        info_lbl = ttk.Label(frame, text="提示: 设置种子>0保证实验完美复现，设为0则使用时间随机种子", foreground="gray")
        info_lbl.grid(row=4, column=0, columnspan=4, pady=5)

        # 运行按钮
        btn = ttk.Button(frame, text="开始训练 (Start Training)", command=self._on_train_click)
        btn.grid(row=5, column=0, columnspan=5, ipadx=20, ipady=10, pady=20)

        # 初始化时加载一次数据集
        self._refresh_dataset_list()

    def _refresh_dataset_list(self):
        """扫描 dataset/ 目录下生成的文件夹"""
        ds_path = os.path.join("dataset")
        if os.path.exists(ds_path):
            dirs = [d for d in os.listdir(ds_path) if
                    os.path.isdir(os.path.join(ds_path, d)) and (d.startswith("Cifar") or d.startswith("MNIST"))]
            self.combo_dataset['values'] = sorted(dirs)
            if dirs:
                self.combo_dataset.current(0)
            else:
                self.tr_dataset.set("未找到数据集，请先生成")
        else:
            self.tr_dataset.set("dataset 目录不存在")

    def _on_train_click(self):

        script = "main.py"

        # 检查文件是否存在 (拼接完整路径进行检查)
        # 这里的检查路径是：当前路径/system/main.py
        check_path = os.path.join(os.getcwd(), "system", script)
        if not os.path.exists(check_path):
            messagebox.showerror("错误", f"找不到文件: {check_path}\n请确认您的目录结构正确。")
            return

        dataset_name = self.tr_dataset.get()
        if not dataset_name or "未找到" in dataset_name:
            messagebox.showwarning("警告", "请先选择一个有效的数据集")
            return

        cmd = [
            sys.executable,
            script,  # 这里只传 "main.py"
            "-data", dataset_name,
            "-algo", self.tr_algo.get(),
            "-m", self.tr_model.get(),
            "-gr", self.tr_gr.get(),
            "-did", self.tr_did.get(),
            "-seed", self.tr_seed.get()
        ]

        cwd_path = os.path.join(os.getcwd(), "system")

        self._run_command(cmd, cwd=cwd_path)

    # ================= 结果对比界面 =================
    def _init_compare_tab(self):
        frame = ttk.Frame(self.tab_compare, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        grid_opts = {'padx': 5, 'pady': 10, 'sticky': 'w'}

        ttk.Label(frame, text="选择要对比的数据集实验组:").grid(row=0, column=0, **grid_opts)
        self.comp_dataset = tk.StringVar()
        self.combo_comp_dataset = ttk.Combobox(frame, textvariable=self.comp_dataset, width=40, state="readonly")
        self.combo_comp_dataset.grid(row=0, column=1, **grid_opts)

        ttk.Button(frame, text="刷新列表", command=self._refresh_comp_list).grid(row=0, column=2, padx=5)

        btn = ttk.Button(frame, text="生成并查看对比图 (Compare Algorithms)", command=self._on_compare_click)
        btn.grid(row=1, column=0, columnspan=3, pady=20, ipadx=20, ipady=10)

        # 启动时自动刷新
        self._refresh_comp_list()

    def _refresh_comp_list(self):
        results_dir = "results"
        if not os.path.exists(results_dir):
            return
        
        datasets = set()
        for d in os.listdir(results_dir):
            if os.path.isdir(os.path.join(results_dir, d)):
                parts = d.rsplit('_', 3)
                if len(parts) >= 3:
                    ds_name = parts[0]
                    datasets.add(ds_name)
                    
        self.combo_comp_dataset['values'] = sorted(list(datasets))
        if datasets:
            self.combo_comp_dataset.current(0)

    def _on_compare_click(self):
        ds_target = self.comp_dataset.get()
        if not ds_target:
            messagebox.showwarning("警告", "请选择要对比的数据集")
            return
        
        results_dir = "results"
        try:
            import h5py
            import matplotlib.pyplot as plt
        except ImportError:
            messagebox.showerror("错误", "缺少必要的库 h5py 或 matplotlib，无法生成对比图。")
            return

        # 寻找该数据集下，所有算法的最新实验结果
        algo_files = {}
        for d in os.listdir(results_dir):
            dir_path = os.path.join(results_dir, d)
            if os.path.isdir(dir_path) and d.startswith(ds_target + "_"):
                parts = d.rsplit('_', 3)
                if len(parts) >= 3 and parts[0] == ds_target:
                    algo = parts[-3]
                    h5_path = os.path.join(dir_path, f"{d}.h5")
                    if os.path.exists(h5_path):
                        # 保留最新的一次结果（时间戳比较）
                        if algo not in algo_files or d > algo_files[algo][0]:
                            algo_files[algo] = (d, h5_path)
        
        if not algo_files:
            messagebox.showinfo("提示", "未找到该数据集的任何实验结果")
            return

        # --- 新增：在控制台打印数值型最终比较表格 ---
        self._log(f"\n====================== 实验结果最终指标对比 ======================")
        self._log(f"数据集: {ds_target}")
        self._log(f"{'算法 (Algorithm)':<15} | {'最佳整体准确率':<15} | {'最佳尾部准确率':<15} | {'最小类间方差':<15}")
        self._log("-" * 75)

        for algo, (d, h5_path) in algo_files.items():
            best_g, best_t, min_v = "-", "-", "-"
            with h5py.File(h5_path, 'r') as hf:
                if 'rs_global_acc' in hf and len(hf['rs_global_acc']) > 0:
                    best_g = f"{max(hf['rs_global_acc'][:]):.4f}"
                if 'rs_tail_acc' in hf and len(hf['rs_tail_acc']) > 0:
                    best_t = f"{max(hf['rs_tail_acc'][:]):.4f}"
                if 'rs_acc_var' in hf and len(hf['rs_acc_var']) > 0:
                    min_v = f"{min(hf['rs_acc_var'][:]):.4f}"
            
            self._log(f"{algo:<20} | {best_g:<22} | {best_t:<22} | {min_v:<20}")
        self._log("==================================================================\n")
        # ------------------------------------------------------------
            
        plt.figure(figsize=(18, 5))
        
        # Plot 1: 整体准确率
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
        
        # Plot 2: 尾部类别平均准确率
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
        
        # Plot 3: 类间准确率方差
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
        save_path = os.path.join(results_dir, f"Comparison_{ds_target}.png")
        plt.savefig(save_path, dpi=300)
        
        self._log(f">>> 对比图已生成: {save_path}")
        
        # 自动打开生成的对比图
        if sys.platform == 'win32':
            os.startfile(save_path)
        elif sys.platform == 'darwin':
            subprocess.call(['open', save_path])
        else:
            subprocess.call(['xdg-open', save_path])

if __name__ == "__main__":
    root = tk.Tk()
    app = LongTailLibGUI(root)
    root.mainloop()
