# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QListWidgetItem, QCompleter, QMenu, QAction, QPushButton, QFileDialog, QShortcut
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence
from PyQt5.QtCore import Qt, QEvent, QItemSelectionModel, QTimer
from sqlite import Sqlite
from pathlib import Path
# from aupyom import Sampler, Sound
import music_tools
# import pkg_resources
import vlc
import os

try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    myappid = 'mycompany.myproduct.subproduct.version'
    QtWin.setCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class Main_window(QMainWindow):

    sqlite = Sqlite()
    current_working_song_id = 0
    current_song = []
    current_song_file = ""
    working_status = "preview"
    fullscreen_status = False
    current_song_tags_buttons = []
    current_song_tags = set()
    gray = "#e3e3e3"
    # os.environ["VLC_PLUGIN_PATH"] = "/usr/lib/x86_64-linux-gnu/vlc/plugins/"
    os.environ["VLC_PLUGIN_PATH"] = "./plugins/"

    def pkg_sound(self, filepath):
        return pkg_resources.resource_filename(__name__, filepath)

    def stop(self):
        """Stop player
        """
        self.mediaplayer.stop()
        self.playbutton.setIcon(self.icon_play)

    def create_icon(self, icon_path_string):
        icons_path = Path("icons/")
        icon_path = icons_path / icon_path_string
        return QIcon(str(icon_path))

    def play_pause(self):
        """Toggle play/pause status
        """
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            # self.playbutton.setText("Play")
            self.is_paused = True
            self.timer.stop()
            self.playbutton.setIcon(self.icon_play)
        else:
            if self.mediaplayer.play() == -1:
                self.open_file()
                return

            self.mediaplayer.play()
            # self.playbutton.setText("Pause")
            self.playbutton.setIcon(self.icon_pause)
            self.timer.start()
            self.is_paused = False

    def load_file(self, filename):
        if filename is None or filename == "":
            self.lb_file_name.setText("")
            self.stop()
            return
        else:
            self.media = self.instance.media_new(filename)
            self.mediaplayer.set_media(self.media)
            self.media.parse()
            self.media_duration = '%.1f'%(self.media.get_duration() / 1000)
            # minutes = int(media_duration / 60)
            # seconds = int(media_duration % 60)
            self.ln_stop_time.setText(self.media_duration)
            self.lb_file_name.setText(self.media.get_meta(0))
            self.stop()
            # self.sqlite.update_song_file(self.current_working_song_id, filename[0])

    def open_file(self):
        """Open a media file in a MediaPlayer
        """

        dialog_txt = "Choose Media File"
        filename = QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename:
            return

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(filename[0])
        self.current_song_file = filename[0]

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as window title
        self.lb_file_name.setText(self.media.get_meta(0))
        if len(filename[0]) > 1:
            self.sqlite.update_song_file(self.current_working_song_id, filename[0])
        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        # if platform.system() == "Linux":  # for Linux using the X Server
        #     self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        # elif platform.system() == "Windows":  # for Windows
        #     self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        # elif platform.system() == "Darwin":  # for MacOS
        #     self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        self.play_pause()

    def update_ui(self):
        """Updates the user interface"""

        # Set the slider's position to its corresponding media position
        # Note that the setValue function only takes values of type int,
        # so we must first convert the corresponding media position.
        media_pos = int(self.mediaplayer.get_position() * 1000)
        media_time = self.mediaplayer.get_time() / 1000
        minutes = int(media_time / 60)
        seconds = int(media_time % 60)
        # print(f"{media_time} {minutes}:{seconds}")
        self.lb_time.setText(f"{minutes}:{seconds}s")
        self.positionslider.setValue(media_pos)

        # No need to call this function if nothing is played
        if not self.mediaplayer.is_playing():
            self.timer.stop()

            # After the video finished, the play button stills shows "Pause",
            # which is not the desired behavior of a media player.
            # This fixes that "bug".
            if not self.is_paused:
                self.stop()

    def set_position(self):
        """Set the movie position according to the position slider.
        """

        # The vlc MediaPlayer needs a float value between 0 and 1, Qt uses
        # integer variables, so you need a factor; the higher the factor, the
        # more precise are the results (1000 should suffice).

        # Set the media position to where the slider was dragged
        self.timer.stop()
        pos = self.positionslider.value()
        self.mediaplayer.set_position(pos / 1000.0)
        self.timer.start()

    # def loop_buttons_clicked(self):
    #     sender = self.sender()
    #     print(sender.objectName())
    #     media_time = '%.1f' % (self.mediaplayer.get_time() / 1000)
    #     if sender.objectName() == "btn_start_time":
    #         start_time = media_time
    #         self.ln_start_time.setText(str(start_time))
    #     elif sender.objectName() == "btn_stop_time":
    #         stop_time = media_time
    #         self.ln_stop_time.setText(str(stop_time))
    #     elif sender.objectName() == "btn_reset_loop":
    #         # self.media.add_option(f"start-time={0.0}")
    #         # self.media.add_option(f"stop-time={self.media_duration}")
    #         # self.media.add_option(f"input-repeat=21")
    #         # # self.media.add_option(f"pitch-shift=5")
    #         # self.mediaplayer.set_media(self.media)
    #         # self.ln_start_time.setText("0.0")
    #         self.ln_stop_time.setText(self.media_duration)

    def set_loop(self):
        start_time = self.ln_start_time.text()
        stop_time = self.ln_stop_time.text()
        sender = self.sender()
        print(sender.objectName())
        media_time = '%.1f' % (self.mediaplayer.get_time() / 1000)
        if sender.objectName() == "btn_start_time":
            start_time = media_time
            self.ln_start_time.setText(str(start_time))
        elif sender.objectName() == "btn_stop_time":
            stop_time = media_time
            self.ln_stop_time.setText(str(stop_time))
        elif sender.objectName() == "ln_start_time":
            print("Interacted with start time line edit")
            start_time = self.ln_start_time.text()
        elif sender.objectName() == "ln_stop_time":
            print("Interacted with stop time line edit")
            stop_time = self.ln_stop_time.text()
        elif sender.objectName() == "btn_reset_loop":
            start_time = 0.0
            self.ln_start_time.setText("0.0")
            stop_time = float(self.media_duration) - 1
            self.ln_stop_time.setText(str(stop_time))
        was_playing = False
        if self.mediaplayer.is_playing(): was_playing = True
        print(f"Start: {start_time} Stop: {stop_time}")
        self.media = self.instance.media_new(self.current_song_file)
        self.media.add_options(f"start-time={start_time}", f"stop-time={stop_time}")
        self.media.add_option(f"input-repeat=21")
        # self.media.add_option(f"pitch-shift=5")
        # self.mediaplayer.set_media(self.media)
        self.mediaplayer.set_media(self.media)
        self.mediaplayer.stop()
        if was_playing:
            self.play_pause()
        # self.mediaplayer.play()

    def __init__(self):
        super().__init__()
        self.icon_edit = self.create_icon("edit.svg")
        self.icon_save = self.create_icon("save.svg")
        self.icon_maximize = self.create_icon("maximize.svg")
        self.icon_minimize = self.create_icon("minimize.svg")
        self.icon_play = self.create_icon("play.svg")
        self.icon_pause = self.create_icon("pause.svg")
        self.icon_folder = self.create_icon("folder.svg")

        uic.loadUi("main_window.ui", self)
        # self.song_area.
        self.btn_edit.setEnabled(False)
        self.ln_artist.setReadOnly(True)
        self.ln_title.setReadOnly(True)
        self.text_song.setReadOnly(True)
        self.ln_tags.setReadOnly(True)
        self.ln_original_tone.setReadOnly(True)
        self.playbutton.setEnabled(False)
        self.btn_open_file.setEnabled(False)
        self.btn_start_time.setEnabled(False)
        self.btn_stop_time.setEnabled(False)
        self.btn_reset_loop.setEnabled(False)
        self.btn_transpose_down.setEnabled(False)
        self.btn_transpose_up.setEnabled(False)
        self.btn_notation.setEnabled(False)
        self.ln_start_time.setReadOnly(True)
        self.ln_stop_time.setReadOnly(True)


        self.ln_artist.setStyleSheet(f"background-color: {self.gray};")
        self.ln_title.setStyleSheet("background-color: lightgrey;")
        self.text_song.setStyleSheet("background-color: lightgrey;")
        self.ln_tags.setStyleSheet("background-color: lightgrey;")
        self.ln_original_tone.setStyleSheet("background-color: lightgrey;")
        # app.setWindowIcon(QtGui.QIcon(':/icons/logo.ico'))

        artist_completer = QCompleter(self.sqlite.get_artists())
        artist_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.ln_artist.setCompleter(artist_completer)
        # self.set_tag_completer()
        self.tag_completer = QCompleter(self.sqlite.get_tags())
        self.tag_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.ln_tags.setCompleter(self.tag_completer)
        print("test")
        self.tag_completer.activated.connect(lambda: self.create_tag(self.ln_tags.text() + " "))
        # self.ln_tags.textChanged.connect()

        # self.sm = self.tag_completer.popup().selectionModel()
        # self.tag_completer.popup().setSelectionModel(self.sm)
        # self.sm.select(self.tag_completer.completionModel().index(0, 0), QItemSelectionModel.Select)


        self.btn_create_song.clicked.connect(self.open_create_new_song_dialog)
        self.btn_fullscreen.clicked.connect(self.fullscreen)
        self.btn_transpose_down.clicked.connect(self.transpose)
        self.btn_transpose_up.clicked.connect(self.transpose)
        self.btn_edit.clicked.connect(self.edit_song)
        self.ln_search.textChanged.connect(lambda: self.search(self.ln_search.text()))
        self.ln_start_time.returnPressed.connect(self.set_loop)
        self.ln_start_time.editingFinished.connect(self.set_loop)
        self.ln_stop_time.returnPressed.connect(self.set_loop)
        self.ln_stop_time.editingFinished.connect(self.set_loop)
        self.btn_start_time.clicked.connect(self.set_loop)
        self.btn_stop_time.clicked.connect(self.set_loop)
        self.btn_reset_loop.clicked.connect(self.set_loop)
        self.ln_tags.textChanged.connect(lambda: self.create_tag(self.ln_tags.text()))
        self.ls_songs.currentItemChanged.connect(self.select_song)

        self.ls_songs.installEventFilter(self)
        # self.ls_songs.setContextMenuPolicy(Qt.ActionsContextMenu)
        # delete_action = QAction("Delete", None)
        # delete_action.triggered.connect(self.delete_song)
        # self.ls_songs.addAction(delete_action)

        songs = self.sqlite.get_songs()
        for song in songs:
            # self.sqlite.get_songs(, )
            list_item = QListWidgetItem(f"{song[1]} - {song[2]}", parent=self.ls_songs)
            list_item.setData(32, {"id":song[0], "tags":song[8]})
            self.ls_songs.insertItem(0, list_item)

        self.instance = vlc.Instance()
        self.is_paused = False
        self.media = None
        self.positionslider.setMaximum(1000)
        self.positionslider.sliderMoved.connect(self.set_position)
        self.positionslider.sliderPressed.connect(self.set_position)
        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)
        self.mediaplayer = self.instance.media_player_new()
        self.playbutton.clicked.connect(self.play_pause)
        self.btn_open_file.clicked.connect(self.open_file)
        # p = vlc.MediaPlayer("3 Doors Down - Loser.mp3")

        # p.play()

        self.msgSc = QShortcut(QKeySequence('Ctrl+Space'), self)
        self.msgSc.activated.connect(self.play_pause)
        self.msgSc = QShortcut(QKeySequence('Ctrl+S'), self)
        self.msgSc.activated.connect(self.edit_song)


    def create_tag(self, text):
        try:
            sqlite = Sqlite()
            # self.tag_completer.setCurrentRow(1)
            # self.sm.select(self.tag_completer.completionModel().index(0, 0), QItemSelectionModel.Select)
            if len(text) < 1:
                return
            elif text == " " or text == ",":
                self.ln_tags.clear()
            elif text[-1] == " " or text[-1] == ",":
                text = text.replace(" ", "")
                text = text.replace(",", "")
                tag_id = sqlite.insert_tag(text)
                # button_tag = QPushButton(text)
                for tag in self.current_song_tags_buttons:
                    self.current_song_tags.add(tag.text())
                    if tag.text() == text:
                        self.ln_tags.clear()
                        return
                self.current_song_tags.add(text)
                self.current_song_tags_buttons.append(QPushButton(text))
                self.current_song_tags_buttons[-1].clicked.connect(self.edit_tag_button)
                self.tags_layout.insertWidget(len(self.current_song_tags_buttons) - 1, self.current_song_tags_buttons[-1])
                # self.ln_tags.clear()
                QTimer.singleShot(0, self.ln_tags.clear)
                self.set_tag_completer()
                print(f"Tags: {self.current_song_tags}")
        except Exception as e:
            print(f"Error: {e}")


    def fullscreen(self):
        if self.fullscreen_status == False:
            self.ln_artist.hide()
            self.lb_artist.hide()
            self.ln_title.hide()
            self.lb_title.hide()
            self.ln_original_tone.hide()
            self.lb_original_tone.hide()
            self.lb_tags.hide()
            self.ln_tags.hide()
            for button in self.current_song_tags_buttons:
                button.hide()
            self.btn_fullscreen.setIcon(self.icon_minimize)
            self.fullscreen_status = True
        else:
            self.ln_artist.show()
            self.lb_artist.show()
            self.ln_title.show()
            self.lb_title.show()
            self.ln_original_tone.show()
            self.lb_original_tone.show()
            self.lb_tags.show()
            self.ln_tags.show()
            for button in self.current_song_tags_buttons:
                button.show()
            self.btn_fullscreen.setIcon(self.icon_maximize)
            self.fullscreen_status = False

    def eventFilter(self, source, event):
        if (event.type() == QEvent.ContextMenu and
                source is self.ls_songs):
            menu = QMenu()
            delete_action = QAction("Delete", None)
            delete_action.triggered.connect(self.delete_song)
            menu.addAction(delete_action)
            if menu.exec_(event.globalPos()):
                item = source.itemAt(event.pos())
                # print(item.text())
            return True
        return super(Main_window, self).eventFilter(source, event)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)
        delete_action = contextMenu.addAction("Delete")


    def delete_song(self):
        self.sqlite.delete_song(self.current_working_song_id)
        self.ls_songs.takeItem(self.ls_songs.currentRow())

        # selected_songs = self.ls_songs.selectedItems()
        # for selected_song in selected_songs:
        #     self.ls_songs.takeItem(self.ls_songs.currentRow())

    def transpose(self):
        sender = self.sender()
        print(sender.objectName())
        if sender.objectName() == "btn_transpose_down": self.lb_user_tone.setText(str(int(self.lb_user_tone.text())-1))
        if sender.objectName() == "btn_transpose_up": self.lb_user_tone.setText(str(int(self.lb_user_tone.text())+1))
        song = self.text_song.toPlainText()
        transposition_semitones = int(self.lb_user_tone.text())
        transposed_song = music_tools.transpose(self.current_song[2], transposition_semitones)
        self.sqlite.update_user_tone(self.ls_songs.currentItem().data(32)['id'], self.lb_user_tone.text())
        self.text_song.clear()
        self.text_song.insertPlainText(transposed_song)
        self.sqlite.update_user_tone(self.current_working_song_id, transposition_semitones)

    def edit_song(self):
        if self.fullscreen_status == True:
            self.fullscreen()
        if(self.working_status == "edit"):
            self.change_widget_status(self.ln_artist)
            self.change_widget_status(self.ln_title)
            self.change_widget_status(self.text_song)
            self.change_widget_status(self.ln_tags)
            self.change_widget_status(self.ln_original_tone)
            self.change_widget_status(self.btn_transpose_down)
            self.change_widget_status(self.btn_transpose_up)
            self.change_widget_status(self.btn_notation)
            self.change_widget_status(self.btn_create_song)
            self.change_widget_status(self.ls_songs)
            for button in self.current_song_tags_buttons:
                self.change_widget_status(button)
            self.btn_edit.setIcon(self.icon_edit)
            self.sqlite.update_song(self.current_working_song_id, self.ln_artist.text(), self.ln_title.text(),
                                    self.text_song.toPlainText(), self.ln_original_tone.text(),
                                    " ".join(self.current_song_tags))
            list_item = self.ls_songs.currentItem()
            self.current_song = self.sqlite.get_song_by_id(self.current_working_song_id)
            # self.current_song[2] = self.text_song.toPlainText()
            self.text_song.setText(music_tools.transpose(self.text_song.toPlainText(), self.current_song[4]))
            self.lb_user_tone.setText(str(self.current_song[4]))
            self.ln_tags.setText("")
            # list_item.data(32)["tags"] = self.ln_tags.text()
            list_item.setText(f"{self.ln_artist.text()} - {self.ln_title.text()}")
            list_item.setData(32, {"id": self.current_working_song_id, "tags": " ".join(self.current_song_tags)})
            # self.current_song = self.text_song.toPlainText()
            self.working_status = "preview"
        elif (self.working_status == "preview"):
            self.change_widget_status(self.ln_artist)
            self.change_widget_status(self.ln_title)
            self.change_widget_status(self.text_song)
            self.change_widget_status(self.ln_tags)
            self.change_widget_status(self.ln_original_tone)
            self.change_widget_status(self.btn_transpose_down)
            self.change_widget_status(self.btn_transpose_up)
            self.change_widget_status(self.btn_notation)
            self.change_widget_status(self.btn_create_song)
            self.change_widget_status(self.ls_songs)
            self.lb_user_tone.setText("0")
            self.text_song.setText(self.current_song[2])
            for button in self.current_song_tags_buttons:
                self.change_widget_status(button)
            # self.ls_songs.viewport().setAttribute(Qt.WA_TransparentForMouseEvents)
            # self.ls_songs.setStyleSheet("background-color: lightgrey;")
            self.btn_edit.setIcon(self.icon_save)
            self.working_status = "edit"
        print(f"Current working status: {self.working_status}")

    def change_widget_status(self, widget):
        print(widget.__class__.__name__)
        if widget.__class__.__name__ == "QPushButton":
            if widget.isEnabled():
                print(f"{widget.__class__.__name__} was enabbled, deactiating it")
                widget.setEnabled(False)
                widget.setStyleSheet("background-color: lightgrey;")
            else:
                print(f"{widget.__class__.__name__} was disabled, activatin it")
                widget.setEnabled(True)
                widget.setStyleSheet("background-color: white;")
        if widget.__class__.__name__ == "QLineEdit":
            if widget.isReadOnly():
                print(f"{widget.__class__.__name__} was enabled, deactivating it")
                widget.setReadOnly(False)
                widget.setStyleSheet("background-color: white;")
            else:
                print(f"{widget.__class__.__name__} was disabled, activatin it")
                widget.setReadOnly(True)
                widget.setStyleSheet("background-color: lightgrey;")
        if widget.__class__.__name__ == "QTextEdit":
            if widget.isReadOnly():
                print(f"{widget.__class__.__name__} was enabled, deactivating it")
                widget.setReadOnly(False)
                widget.setStyleSheet("background-color: white;")
            else:
                print(f"{widget.__class__.__name__} was disabled, activatin it")
                widget.setReadOnly(True)
                widget.setStyleSheet("background-color: lightgrey;")
        if widget.__class__.__name__ == "QListWidget":
            if widget.viewport().testAttribute(Qt.WA_TransparentForMouseEvents):
                print(f"{widget.__class__.__name__} was enabled, deactivating it")
                self.ls_songs.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, False)
                widget.setStyleSheet("background-color: white;")
            else:
                print(f"{widget.__class__.__name__} was disabled, activatin it")
                self.ls_songs.viewport().setAttribute(Qt.WA_TransparentForMouseEvents, True)
                widget.setStyleSheet("background-color: lightgrey;")

    def select_song(self):
        # print(self.ls_songs.selectedItems()[0][0])
        # print(self.ls_songs.selectedItems()[0][0].text())
        # ls_item = self.ls_songs.selectedItems(self.ls_songs.selectedItems()[0][0].text())
        # self.ls_songs.setCurrentItem(ls_item)

        if self.ls_songs.currentItem().data(32) is None:
            return
        self.btn_edit.setEnabled(True)
        self.playbutton.setEnabled(True)
        self.btn_open_file.setEnabled(True)
        self.btn_start_time.setEnabled(True)
        self.btn_stop_time.setEnabled(True)
        self.btn_reset_loop.setEnabled(True)
        self.btn_transpose_down.setEnabled(True)
        self.btn_transpose_up.setEnabled(True)
        self.btn_notation.setEnabled(True)
        self.ln_start_time.setReadOnly(False)
        self.ln_stop_time.setReadOnly(False)
        self.current_working_song_id = self.ls_songs.currentItem().data(32)["id"]
        song = self.sqlite.get_song_by_id(self.current_working_song_id)
        print(f"Data: {self.ls_songs.currentItem().data(32)}")
        self.current_song = song
        self.current_song_file = song[8]
        self.ln_title.setText(song[1])
        self.ln_artist.setText(song[0])
        self.lb_user_tone.setText(str(song[4]))
        self.clear_tags()
        self.load_file(song[8])
        self.mediaplayer.stop()
        if str(song[7]) != "None" and str(song[7]) != " " and str(song[7]) != "":
            tags = song[7].split(" ")
            self.current_song_tags = set(tags)
            for tag in tags:
                self.current_song_tags_buttons.append(QPushButton(tag))
                self.current_song_tags_buttons[-1].clicked.connect(self.edit_tag_button)
                self.change_widget_status(self.current_song_tags_buttons[-1])
                self.tags_layout.insertWidget(len(self.current_song_tags_buttons) - 1, self.current_song_tags_buttons[-1])

            # self.ln_tags.setText(str(song[7]))
        else:
            self.ln_tags.setText("")
        if self.lb_user_tone.text() != "0":
            self.text_song.setText(music_tools.transpose(song[2], self.lb_user_tone.text()))
        else:
            self.text_song.setText(song[2])

    def edit_tag_button(self):
        sqlite = Sqlite()
        button = self.sender()
        tag = button.text()
        self.current_song_tags_buttons.remove(button)
        self.current_song_tags.remove(button.text())

        self.sqlite.update_song(self.current_working_song_id, self.ln_artist.text(), self.ln_title.text(),
                                self.text_song.toPlainText(), self.ln_original_tone.text(),
                                " ".join(self.current_song_tags))
        if len(sqlite.select_song_by_tag(tag)) < 1:
            sqlite.delete_tag(tag)
        button.deleteLater()



    def clear_tags(self):
        print(f"Tags: {self.current_song_tags}")
        print(f"Tags buttons: {self.current_song_tags_buttons}")
        if len(self.current_song_tags_buttons) > 0:
            for tag_button in self.current_song_tags_buttons:
                tag_button.deleteLater()
                self.current_song_tags.clear()
            self.current_song_tags_buttons.clear()

    def open_create_new_song_dialog(self):
        # create_new_song_d = create_new_song_dialog(self)
        # create_new_song_d.show()
        create_new_song_d = create_new_song_dialog(self)
        create_new_song_d.setModal(True)
        create_new_song_d.exec()
        # print("AAAAAAAAa")
        # QTimer.singleShot(1, self.select_song)

    def search(self, text):
        for row in range(self.ls_songs.count()):
            it = self.ls_songs.item(row)
            tags = ""
            # widget = self.ui.catalog_list_wid.itemWidget(it)
            if text:
                print(it.text())

                if it.data(32)['tags'] is not None:
                    tags = it.data(32)['tags']
                else:
                    tags = ""
                it.setHidden(not text.lower() in f"{it.text().lower()} {tags.lower()}")
                print(f"{it.text().lower()} {tags.lower()}")
            else:
                it.setHidden(False)

class create_new_song_dialog(QDialog):

    sqlite = Sqlite()
    mw = None

    def __init__(self, main_window):
        super().__init__()
        artist_completer = QCompleter(self.sqlite.get_artists())
        artist_completer.setCaseSensitivity(Qt.CaseInsensitive)
        uic.loadUi("create_song.ui", self)
        self.btn_cancel.clicked.connect(self.close)
        self.btn_create.clicked.connect(self.create_song)
        self.ln_artist.setCompleter(artist_completer)
        self.mw = main_window


    def create_song(self):
        artist = self.ln_artist.text()
        title = self.ln_title.text()
        song_id = self.sqlite.insert_song(artist, title)
        list_item = QListWidgetItem(f"{artist} - {title}", parent=self.mw.ls_songs)
        list_item.setData(32, {"id":song_id,"tags":""})
        list_item.setSelected(True)
        self.mw.ls_songs.insertItem(0, list_item)
        # self.mw.ls_songs.setCurrentItem( list_item)
        list_item.setSelected(True)
        self.mw.ls_songs.setCurrentItem(list_item)
        self.mw.ln_title.setText(title)
        self.mw.ln_artist.setText(artist)
        self.mw.ln_original_tone.setText("")
        self.mw.text_song.setText("")
        self.mw.ln_tags.setText("")
        self.mw.btn_edit.setEnabled(True)
        self.mw.select_song()
        self.close()





# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = Main_window()
    main_window.show()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
