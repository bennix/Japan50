import sys
import asyncio
import edge_tts
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
from playsound import playsound
import random

class GojuonTable(QMainWindow):
    def __init__(self):
        super().__init__()
        # 添加音频缓存字典
        self.audio_cache = {}
        # 添加缓存目录
        self.cache_dir = os.path.join(os.path.dirname(__file__), 'audio_cache')
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.initUI()
        
    def initUI(self):
        # 主窗口设置
        self.setWindowTitle('五十音图学习')
        self.setGeometry(100, 100, 800, 600)
        
        # 创建中心部件和网格布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        grid = QGridLayout(central_widget)
        
        # 五十音数据
        self.gojuon = [
            ['あ', 'い', 'う', 'え', 'お'],
            ['か', 'き', 'く', 'け', 'こ'],
            ['さ', 'し', 'す', 'せ', 'そ'],
            ['た', 'ち', 'つ', 'て', 'と'],
            ['な', 'に', 'ぬ', 'ね', 'の'],
            ['は', 'ひ', 'ふ', 'へ', 'ほ'],
            ['ま', 'み', 'む', 'め', 'も'],
            ['や', 'い', 'ゆ', 'え', 'よ'],
            ['ら', 'り', 'る', 'れ', 'ろ'],
            ['わ', 'い', 'う', 'え', 'を'],
            ['ん', '', '', '', '']
        ]
        
        # 创建按钮网格
        for i, row in enumerate(self.gojuon):
            for j, kana in enumerate(row):
                if kana:
                    btn = QPushButton(kana)
                    # 设置日语字体
                    font = QFont("Yu Gothic", 20)
                    btn.setFont(font)
                    btn.setFixedSize(60, 60)
                    btn.clicked.connect(lambda ch, k=kana: self.play_sound(k))
                    grid.addWidget(btn, i, j)
                    
        # 添加测试按钮
        self.test_button = QPushButton('听力测试', self)
        self.test_button.clicked.connect(self.openTestWindow)
        # 将测试按钮添加到布局中的适当位置
        
    def play_sound(self, kana):
        # 检查缓存中是否存在
        cache_file = os.path.join(self.cache_dir, f"{kana}.mp3")
        if os.path.exists(cache_file):
            # 直接播放缓存的音频
            playsound(cache_file)
        else:
            # 不存在则生成并缓存
            asyncio.run(self.tts_speak(kana))
        
    async def tts_speak(self, text):
        voice = "ja-JP-NanamiNeural"
        tts = edge_tts.Communicate(text=text, voice=voice)
        # 保存到缓存目录
        cache_file = os.path.join(self.cache_dir, f"{text}.mp3") 
        await tts.save(cache_file)
        playsound(cache_file)
        
    def openTestWindow(self):
        self.test_window = TestWindow(self.cache_dir)
        self.test_window.show()

class TestWindow(QMainWindow):
    def __init__(self, cache_dir, parent=None):
        super().__init__(parent)
        self.cache_dir = cache_dir
        # 五十音数据
        self.gojuon = [
            ['あ', 'い', 'う', 'え', 'お'],
            ['か', 'き', 'く', 'け', 'こ'],
            ['さ', 'し', 'す', 'せ', 'そ'],
            ['た', 'ち', 'つ', 'て', 'と'],
            ['な', 'に', 'ぬ', 'ね', 'の'],
            ['は', 'ひ', 'ふ', 'へ', 'ほ'],
            ['ま', 'み', 'む', 'め', 'も'],
            ['や', 'い', 'ゆ', 'え', 'よ'],
            ['ら', 'り', 'る', 'れ', 'ろ'],
            ['わ', 'い', 'う', 'え', 'を'],
            ['ん', '', '', '', '']
        ]
        self.initUI()
        self.newQuestion()
        
    def initUI(self):
        self.setWindowTitle('五十音听力测试')
        self.setGeometry(200, 200, 400, 300)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 播放按钮
        self.playButton = QPushButton('播放发音')
        self.playButton.clicked.connect(self.playSound)
        layout.addWidget(self.playButton)
        
        # 选项按钮
        self.optionsGroup = QButtonGroup()
        self.optionsLayout = QVBoxLayout()
        
        for i in range(4):
            btn = QPushButton()
            font = QFont("Yu Gothic", 20)
            btn.setFont(font)
            btn.clicked.connect(self.checkAnswer)
            self.optionsGroup.addButton(btn, i)
            self.optionsLayout.addWidget(btn)
            
        layout.addLayout(self.optionsLayout)
        
        # 下一题按钮
        self.nextButton = QPushButton('下一题')
        self.nextButton.clicked.connect(self.newQuestion)
        layout.addWidget(self.nextButton)
        
    def newQuestion(self):
        # 随机选择一个假名作为正确答案
        all_kana = [kana for row in self.gojuon for kana in row if kana]
        self.current_kana = random.choice(all_kana)
        
        # 生成3个错误选项
        wrong_options = random.sample([k for k in all_kana if k != self.current_kana], 3)
        options = wrong_options + [self.current_kana]
        random.shuffle(options)
        
        # 记录正确答案的位置
        self.correct_answer = options.index(self.current_kana)
        
        # 设置选项按钮文本
        for i, option in enumerate(options):
            self.optionsGroup.button(i).setText(option)
            self.optionsGroup.button(i).setStyleSheet('')
            
        # 自动播放当前假名的音频
        QTimer.singleShot(500, self.playSound)  # 延迟500毫秒后播放
        
    def playSound(self):
        # 播放当前假名的音频
        cache_file = os.path.join(self.cache_dir, f"{self.current_kana}.mp3")
        if os.path.exists(cache_file):
            playsound(cache_file)
            
    def checkAnswer(self):
        # 检查答案
        clicked_button = self.sender()
        clicked_id = self.optionsGroup.id(clicked_button)
        
        if clicked_id == self.correct_answer:
            clicked_button.setStyleSheet('background-color: lightgreen')
        else:
            clicked_button.setStyleSheet('background-color: pink')
            correct_button = self.optionsGroup.button(self.correct_answer)
            correct_button.setStyleSheet('background-color: lightgreen')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GojuonTable()
    ex.show()
    sys.exit(app.exec_())
