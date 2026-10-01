import time
import sys

# ============ macOS 原生鼠标控制 (Quartz) ============
import Quartz
from Quartz import (
    CGEventCreateMouseEvent, CGEventPost,
    kCGHIDEventTap,
    kCGEventLeftMouseDown, kCGEventLeftMouseUp,
    kCGMouseButtonLeft,
    kCGEventMouseMoved,
)

def _post_mouse_event(event_type, x, y):
    """发送鼠标事件到系统"""
    event = CGEventCreateMouseEvent(None, event_type, (x, y), kCGMouseButtonLeft)
    CGEventPost(kCGHIDEventTap, event)

def move_mouse(x, y):
    """移动鼠标到指定位置"""
    _post_mouse_event(kCGEventMouseMoved, x, y)

def click(x, y):
    """在指定位置点击一次（Quartz 原生，快且稳）"""
    _post_mouse_event(kCGEventMouseMoved, x, y)
    time.sleep(0.02)
    _post_mouse_event(kCGEventLeftMouseDown, x, y)
    time.sleep(0.02)
    _post_mouse_event(kCGEventLeftMouseUp, x, y)

def get_mouse_position():
    """获取当前鼠标位置"""
    event = Quartz.CGEventCreate(None)
    loc = Quartz.CGEventGetLocation(event)
    return int(loc.x), int(loc.y)


# ============ 自动点击器 ============
class AutoClicker:
    def __init__(self):
        self.stop_flag = False

    def countdown(self, seconds):
        """开始前的倒计时提示"""
        print(f"\n⏳ {seconds} 秒后开始点击，请把鼠标移到目标窗口...")
        for i in range(seconds, 0, -1):
            if self.stop_flag:
                return False
            print(f"   {i}...", end="\r", flush=True)
            time.sleep(1)
        print("   🚀 开始！        ")
        return True

    def click_at_position(self, x, y, duration, interval=0.1):
        """
        在指定时间内重复点击同一位置

        参数:
            x, y      : 点击位置
            duration  : 持续时间（秒）
            interval  : 点击间隔（秒）
        """
        self.stop_flag = False
        start = time.time()
        count = 0

        print(f"📍 目标位置：({x}, {y})")
        print(f"⏱️  持续时间：{duration} 秒")
        print(f"🔁 点击间隔：{interval} 秒")
        print(f"💡 想中途停止，把鼠标快速甩到屏幕【左上角】\n")

        try:
            while time.time() - start < duration:
                # 检测紧急停止：鼠标在屏幕左上角
                mx, my = get_mouse_position()
                if mx < 5 and my < 5:
                    print("\n🛑 检测到鼠标在左上角，紧急停止！")
                    break
                if self.stop_flag:
                    print("\n🛑 用户手动停止")
                    break

                click(x, y)
                count += 1

                elapsed = time.time() - start
                remain = duration - elapsed
                print(f"   已点击 {count} 次 | 剩余 {remain:5.1f}s",
                      end="\r", flush=True)

                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n🛑 收到 Ctrl+C，已停止")

        used = time.time() - start
        print(f"\n\n✅ 结束！共点击 {count} 次，用时 {used:.2f} 秒")
        print(f"   平均频率：{count / used:.1f} 次/秒" if used > 0 else "")

    def stop(self):
        self.stop_flag = True


# ============ 交互式获取参数 ============
def ask_int(prompt, default=None, min_val=1):
    """询问一个整数"""
    while True:
        tip = f"{prompt}"
        if default is not None:
            tip += f" [默认 {default}]"
        tip += "："
        s = input(tip).strip()
        if not s and default is not None:
            return default
        try:
            v = int(s)
            if v < min_val:
                print(f"⚠️  请填大于等于 {min_val} 的数")
                continue
            return v
        except ValueError:
            print("⚠️  请输入一个整数")

def ask_float(prompt, default=None, min_val=0.01):
    """询问一个浮点数"""
    while True:
        tip = f"{prompt}"
        if default is not None:
            tip += f" [默认 {default}]"
        tip += "："
        s = input(tip).strip()
        if not s and default is not None:
            return default
        try:
            v = float(s)
            if v < min_val:
                print(f"⚠️  请填大于等于 {min_val} 的数")
                continue
            return v
        except ValueError:
            print("⚠️  请输入一个数字")


# ============ 主流程 ============
def main():
    print("=" * 52)
    print("  鼠标自动点击器 (macOS Quartz 原生版)")
    print("=" * 52)

    # 1. 选择点击位置
    print("\n【步骤 1】选择点击位置")
    print("  1) 手动输入坐标")
    print("  2) 3 秒后自动捕获鼠标位置（推荐）")
    mode = input("请选择 [1/2，默认 2]：").strip() or "2"

    if mode == "1":
        x = ask_int("请输入 X 坐标", default=500, min_val=0)
        y = ask_int("请输入 Y 坐标", default=300, min_val=0)
    else:
        print("\n  请把鼠标移动到目标位置，3 秒后自动记录...")
        for i in range(3, 0, -1):
            print(f"    {i}...", end="\r", flush=True)
            time.sleep(1)
        x, y = get_mouse_position()
        print(f"   ✅ 已捕获位置：({x}, {y})     ")

    # 2. 设置持续时间
    print("\n【步骤 2】设置点击参数")
    duration = ask_float("点击总时长（秒）", default=10.0, min_val=0.1)
    interval = ask_float("每次点击间隔（秒）", default=0.1, min_val=0.001)

    # 3. 启动前倒计时
    print("\n【步骤 3】准备启动")
    delay = ask_int("几秒后开始点击", default=3, min_val=0)

    clicker = AutoClicker()

    if delay > 0:
        ok = clicker.countdown(delay)
        if not ok:
            print("已取消")
            return

    # 4. 开始点击
    clicker.click_at_position(x, y, duration, interval)


if __name__ == "__main__":
    try:
        import Quartz  # noqa
    except ImportError:
        print("❌ 缺少 Quartz 库，请先安装：")
        print("   pip install pyobjc-framework-Quartz")
        print("   或 conda install -c conda-forge pyobjc-framework-quartz")
        sys.exit(1)

    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 已退出")