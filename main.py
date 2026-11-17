import os, sqlite3, re
from datetime import date, datetime, timedelta
from collections import Counter
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

try:
    from plyer import notification
except Exception:
    notification = None

KV = '''
#:import dp kivy.metrics.dp
#:import get_color_from_hex kivy.utils.get_color_from_hex
<Accent@Button>:
    background_normal: ''
    background_color: 0,0,0,0
    color: 1,1,1,1
    bold: True
    canvas.before:
        Color:
            rgba: get_color_from_hex('#745BFF')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(15)]
<Soft@Button>:
    background_normal: ''
    background_color: 0,0,0,0
    color: get_color_from_hex('#D9D7F2')
    canvas.before:
        Color:
            rgba: get_color_from_hex('#29273F')
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(14)]
<DarkInput@TextInput>:
    size_hint_y: None
    height: dp(48)
    multiline: False
    foreground_color: 1,1,1,1
    hint_text_color: .6,.58,.7,1
    background_normal: ''
    background_active: ''
    background_color: get_color_from_hex('#29273F')
    padding: dp(12)
<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(17)
        spacing: dp(11)
        canvas.before:
            Color:
                rgba: get_color_from_hex('#11111E')
            Rectangle:
                pos: self.pos
                size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(48)
            Label:
                text: '[b]DAYFLOW[/b] [color=9A8BFF]✦[/color]'
                markup: True
                font_size: '23sp'
                halign: 'left'
                text_size: self.size
            Label:
                text: root.day
                color: .65,.63,.78,1
                size_hint_x: .55
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(112)
            padding: dp(15)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#292544')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(20)]
            Label:
                text: '[b]Твой день — твой ритм[/b]'
                markup: True
                font_size: '19sp'
                halign: 'left'
                text_size: self.size
            Label:
                text: root.summary
                color: .75,.72,.88,1
                halign: 'left'
                text_size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(43)
            Label:
                text: '[b]Привычки на сегодня[/b]'
                markup: True
                font_size: '17sp'
                halign: 'left'
                text_size: self.size
            Accent:
                text: '+ Добавить'
                size_hint_x: None
                width: dp(120)
                on_release: root.add_habit()
        ScrollView:
            GridLayout:
                id: habit_list
                cols: 1
                spacing: dp(9)
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: dp(55)
            spacing: dp(6)
            Soft:
                text: '⌂ Главная'
                on_release: app.root.current = 'home'
            Soft:
                text: '◷ Статистика'
                on_release: app.root.current = 'stats'
            Soft:
                text: '✦ AI'
                on_release: app.root.current = 'ai'
            Soft:
                text: '⚙ Ещё'
                on_release: app.root.current = 'more'
<StatsScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: get_color_from_hex('#11111E')
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: '[b]Твоя статистика[/b]'
            markup: True
            font_size: '23sp'
            size_hint_y: None
            height: dp(48)
            halign: 'left'
            text_size: self.size
        BoxLayout:
            size_hint_y: None
            height: dp(90)
            spacing: dp(10)
            Label:
                id: today_stat
                text: '0/0'
                font_size: '25sp'
                color: get_color_from_hex('#9A8BFF')
                canvas.before:
                    Color:
                        rgba: get_color_from_hex('#29273F')
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(16)]
            Label:
                id: rate_stat
                text: '0%'
                font_size: '25sp'
                color: get_color_from_hex('#51D6B3')
                canvas.before:
                    Color:
                        rgba: get_color_from_hex('#29273F')
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [dp(16)]
        Label:
            text: 'Выполнения за 7 дней'
            size_hint_y: None
            height: dp(28)
            color: .7,.68,.82,1
            halign: 'left'
            text_size: self.size
        BoxLayout:
            id: bars
            spacing: dp(8)
            padding: dp(8)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#1D1C2E')
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(16)]
        Label:
            id: categories
            color: .85,.83,.94,1
            halign: 'left'
            valign: 'top'
            text_size: self.size
        Soft:
            text: '← На главную'
            size_hint_y: None
            height: dp(48)
            on_release: app.root.current = 'home'
<AIScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: get_color_from_hex('#11111E')
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: '[b]AI-помощник ✦[/b]'
            markup: True
            font_size: '23sp'
            size_hint_y: None
            height: dp(48)
            halign: 'left'
            text_size: self.size
        Label:
            text: 'Опиши привычку — помощник определит категорию и предложит полезный совет.'
            color: .72,.7,.84,1
            size_hint_y: None
            height: dp(60)
            halign: 'left'
            text_size: self.size
        DarkInput:
            id: ai_name
            hint_text: 'Например: читать 20 минут перед сном'
        Accent:
            text: '✦ Проанализировать'
            size_hint_y: None
            height: dp(50)
            on_release: root.analyze()
        Label:
            id: ai_answer
            text: 'Здесь появится результат'
            color: .9,.88,1,1
            halign: 'left'
            valign: 'top'
            text_size: self.size
        Soft:
            text: '← На главную'
            size_hint_y: None
            height: dp(48)
            on_release: app.root.current = 'home'
<MoreScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(18)
        spacing: dp(12)
        canvas.before:
            Color:
                rgba: get_color_from_hex('#11111E')
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: '[b]Голос и напоминания[/b]'
            markup: True
            font_size: '22sp'
            size_hint_y: None
            height: dp(48)
            halign: 'left'
            text_size: self.size
        Accent:
            text: '🎙 Голосовой ввод'
            size_hint_y: None
            height: dp(52)
            on_release: app.voice()
        Label:
            id: voice_status
            text: 'Голосовой ввод использует системное распознавание Android.'
            color: .75,.72,.88,1
            halign: 'left'
            valign: 'top'
            text_size: self.size
        Label:
            text: 'Напоминания по времени проверяются, пока приложение открыто. Для фоновых уведомлений после закрытия приложения нужен нативный Android AlarmManager.'
            color: .58,.56,.7,1
            font_size: '12sp'
            halign: 'left'
            valign: 'top'
            text_size: self.size
        Soft:
            text: '← На главную'
            size_hint_y: None
            height: dp(48)
            on_release: app.root.current = 'home'
'''

def category(name):
    s = name.lower()
    rules = {
        'Здоровье': ['вода','пить','сон','спать','спорт','трен','бег','заряд','медит'],
        'Обучение': ['учить','слова','язык','читать','книг','курс','англ','учеб'],
        'Продуктивность': ['план','работ','задач','фокус','уборк','дневник'],
        'Забота о себе': ['уход','крем','кожа','отдых','прогул','дых'],
        'Финансы': ['копить','бюджет','деньг','расход','эконом']
    }
    for cat, words in rules.items():
        if any(w in s for w in words): return cat
    return 'Личное'

class Store:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.execute('CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY, name TEXT, cat TEXT, reminder TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS logs(hid INTEGER, day TEXT, done INTEGER, PRIMARY KEY(hid,day))')
        self.db.commit()
    def habits(self):
        return self.db.execute('SELECT * FROM habits ORDER BY id DESC').fetchall()
    def add(self, name, cat, reminder):
        self.db.execute('INSERT INTO habits(name,cat,reminder) VALUES(?,?,?)',(name,cat,reminder)); self.db.commit()
    def toggle(self, hid):
        d=date.today().isoformat()
        r=self.db.execute('SELECT done FROM logs WHERE hid=? AND day=?',(hid,d)).fetchone()
        self.db.execute('INSERT OR REPLACE INTO logs VALUES(?,?,?)',(hid,d,0 if r and r['done'] else 1)); self.db.commit()
    def done(self,hid):
        r=self.db.execute('SELECT done FROM logs WHERE hid=? AND day=?',(hid,date.today().isoformat())).fetchone()
        return bool(r and r['done'])
    def counts(self):
        return len(self.habits()), self.db.execute('SELECT COUNT(*) FROM logs WHERE day=? AND done=1',(date.today().isoformat(),)).fetchone()[0]

class MainScreen(Screen):
    day=StringProperty('')
    summary=StringProperty('')
    def on_pre_enter(self,*a): self.refresh()
    def refresh(self):
        self.day=date.today().strftime('%d.%m.%Y')
        total,done=App.get_running_app().store.counts()
        self.summary=f'Сегодня выполнено {done} из {total}. Каждый маленький шаг имеет значение.'
        box=self.ids.habit_list; box.clear_widgets()
        for h in App.get_running_app().store.habits():
            row=BoxLayout(size_hint_y=None,height=dp(72),spacing=dp(8),padding=dp(10))
            with row.canvas.before:
                from kivy.graphics import Color, RoundedRectangle
                Color(*get_color_from_hex('#29273F')); bg=RoundedRectangle(pos=row.pos,size=row.size,radius=[dp(15)])
            row.bind(pos=lambda x,v,b=bg:setattr(b,'pos',v),size=lambda x,v,b=bg:setattr(b,'size',v))
            info=BoxLayout(orientation='vertical')
            info.add_widget(Label(text='[b]'+h['name']+'[/b]',markup=True,color=(1,1,1,1),halign='left',text_size=(dp(220),None)))
            info.add_widget(Label(text=h['cat']+'  ·  '+(h['reminder'] or 'без напоминания'),font_size='11sp',color=(.65,.63,.78,1),halign='left'))
            row.add_widget(info)
            b=Button(text='✓' if App.get_running_app().store.done(h['id']) else '○',font_size='24sp',size_hint_x=None,width=dp(48),background_normal='',background_color=(0,0,0,0),color=get_color_from_hex('#51D6B3'))
            b.bind(on_release=lambda x,hid=h['id']:self.mark(hid)); row.add_widget(b); box.add_widget(row)
        if not App.get_running_app().store.habits():
            box.add_widget(Label(text='Добавь первую привычку с помощью кнопки выше ✦',color=(.65,.63,.78,1),size_hint_y=None,height=dp(70)))
    def mark(self,hid):
        App.get_running_app().store.toggle(hid); self.refresh()
    def add_habit(self):
        from kivy.uix.textinput import TextInput
        content=BoxLayout(orientation='vertical',spacing=dp(9),padding=dp(12))
        name=TextInput(hint_text='Название привычки',multiline=False,size_hint_y=None,height=dp(46))
        rem=TextInput(hint_text='Время напоминания: 08:30',multiline=False,size_hint_y=None,height=dp(46))
        save=Button(text='Сохранить',size_hint_y=None,height=dp(46),background_normal='',background_color=get_color_from_hex('#745BFF'))
        content.add_widget(name); content.add_widget(rem); content.add_widget(save)
        pop=Popup(title='Новая привычка',content=content,size_hint=(.9,None),height=dp(240))
        def submit(*a):
            n=name.text.strip()
            if not n: return
            r=rem.text.strip()
            if r and not re.match(r'^([01]?\d|2[0-3]):[0-5]\d$',r): r=''
            App.get_running_app().store.add(n,category(n),r); pop.dismiss(); self.refresh()
        save.bind(on_release=submit); pop.open()

class StatsScreen(Screen):
    def on_pre_enter(self,*a):
        store=App.get_running_app().store
        total,done=store.counts()
        self.ids.today_stat.text=f'{done}/{total}\\nсегодня'
        self.ids.rate_stat.text=f'{round(done/total*100) if total else 0}%\\nготово'
        chart=self.ids.bars; chart.clear_widgets()
        vals=[]
        for i in range(6,-1,-1):
            d=(date.today()-timedelta(days=i)).isoformat()
            n=store.db.execute('SELECT COUNT(*) FROM logs WHERE day=? AND done=1',(d,)).fetchone()[0]
            vals.append((d,n))
        mx=max([v for _,v in vals]+[1])
        for d,n in vals:
            col=BoxLayout(orientation='vertical',spacing=dp(4))
            col.add_widget(Label(text=str(n),size_hint_y=None,height=dp(18),font_size='11sp',color=(.7,.68,.82,1)))
            col.add_widget(Label(text='▮'*max(1,round(5*n/mx)) if n else '·',color=get_color_from_hex('#9A8BFF'),font_size='22sp'))
            col.add_widget(Label(text=datetime.fromisoformat(d).strftime('%a'),size_hint_y=None,height=dp(18),font_size='10sp',color=(.65,.63,.78,1)))
            chart.add_widget(col)
        cats=Counter(h['cat'] for h in store.habits())
        self.ids.categories.text='Категории привычек\\n'+'\\n'.join(f'• {k}: {v}' for k,v in cats.most_common())

class AIScreen(Screen):
    def analyze(self):
        n=self.ids.ai_name.text.strip()
        if not n: self.ids.ai_answer.text='Сначала опиши привычку.'; return
        c=category(n)
        tips={'Здоровье':'Начни с небольшой цели и привяжи её к уже существующему ритуалу.','Обучение':'Короткая ежедневная практика эффективнее редких длинных занятий.','Продуктивность':'Выдели постоянное время и заранее определи минимальный результат.','Забота о себе':'Сделай привычку приятным ритуалом.','Финансы':'Записывай результат, чтобы видеть динамику.','Личное':'Сформулируй действие так, чтобы его было легко повторять ежедневно.'}
        self.ids.ai_answer.text=f'✦ Категория: {c}\\n\\nСовет: {tips[c]}\\n\\nЭто локальная интеллектуальная классификация по ключевым словам. Для генеративного ИИ можно подключить API.'

class HabitApp(App):
    def build(self):
        self.store=Store(os.path.join(self.user_data_dir,'dayflow.sqlite3'))
        Builder.load_string(KV)
        sm=ScreenManager(transition=FadeTransition())
        sm.add_widget(MainScreen(name='home')); sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(AIScreen(name='ai')); sm.add_widget(MoreScreen(name='more'))
        Clock.schedule_interval(self.reminders,30)
        return sm
    def reminders(self,dt):
        now=datetime.now().strftime('%H:%M')
        if not hasattr(self,'sent'): self.sent=set()
        for h in self.store.habits():
            key=(h['id'],date.today().isoformat())
            if h['reminder']==now and key not in self.sent:
                self.sent.add(key)
                if notification:
                    try: notification.notify(title='Dayflow',message='Пора: '+h['name'],timeout=10)
                    except Exception: pass
    def voice(self):
        try:
            from jnius import autoclass
            Activity=autoclass('org.kivy.android.PythonActivity')
            Intent=autoclass('android.content.Intent')
            RI=autoclass('android.speech.RecognizerIntent')
            intent=Intent(RI.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RI.EXTRA_LANGUAGE_MODEL,RI.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RI.EXTRA_LANGUAGE,'ru-RU')
            Activity.mActivity.startActivityForResult(intent,7654)
            self.root.get_screen('more').ids.voice_status.text='Открыто системное распознавание речи Android.'
        except Exception:
            self.root.get_screen('more').ids.voice_status.text='Голосовой ввод работает в APK на Android; на компьютере недоступен.'

    def on_activity_result(self, request_code, result_code, data):
        if request_code != 7654 or data is None:
            return
        try:
            from jnius import autoclass
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            results = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if results and results.size() > 0:
                spoken = str(results.get(0))
                cat, _ = suggestion(spoken)
                self.db.add(spoken, cat, '')
                self.root.get_screen('main').refresh()
                self.root.current = 'main'
                self.root.get_screen('settings').ids.voice_result.text = f'Добавлено голосом: {spoken}'
        except Exception:
            self.root.get_screen('settings').ids.voice_result.text = 'Не удалось обработать результат диктовки.'

if __name__ == '__main__':
    HabitApp().run()
