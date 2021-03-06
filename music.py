import sys
from gi.repository import GObject, GLib

# to walk the filesystem
import os
from os import listdir, walk
from os.path import isfile, join, expanduser

# to play songs
from backend import MusicPlayer

# to manage playlist
from playlist_creator import PlaylistManager

# custom Qt Objects
from custom_qt_objects import CustomQWidget, CustomQListWidgetItem, \
                              CustomPlaylistQWidget, CustomQListPlaylistWidgetItem

# to hanlde the Qt GUI
from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import SIGNAL, SLOT, QTimer
from PyQt4.QtGui import QApplication, QMainWindow, QPushButton, \
                         QFileDialog, QListView, QListWidgetItem, QIcon

Ui_MainWindow, QtBaseClass = uic.loadUiType('./gui/frontend.ui')


#class MainWindow(QMainWindow):
class MainWindow(QtGui.QMainWindow, Ui_MainWindow):

     music_path = ""
     def __init__(self):
         QtGui.QMainWindow.__init__(self)
         Ui_MainWindow.__init__(self)
         self.setupUi(self)

         # set the default properties of the volume slider
         self.volumeSlider.setMinimum(0)
         self.volumeSlider.setMaximum(100)
         self.volumeSlider.setValue(50)
         self.volumeSlider.setTickInterval(1)

         # set fake value for the elapsed time slider
         self.elapsedTimeSlider.setMinimum(0)

         # instantiate the MusicPlayer object
         self.player = MusicPlayer()

         #instantiate the PlaylistManager object
         self.playlist_manager = PlaylistManager()

         # setting the methods to be called
         self.playButton.clicked.connect(self.playPauseAudio)
         self.stopButton.clicked.connect(self.stopAudio)
         self.browseButton.clicked.connect(self.browseFs)
         self.volumeSlider.valueChanged.connect(self.changeVolume)

         self.elapsedTimeSlider.sliderReleased.connect(self.seek_song_position)

         self.player.eosReached.connect(self.play_next_song)
         #self.player.playingSet.connect(self.set_song_duration)

         self.songsListWidget.itemDoubleClicked.connect(self.play_song)

         self.playlistListWidget.itemClicked.connect(self.create_playlist_songs_list)

         # set icons for the button
         self.stopButton.setIcon(QtGui.QIcon('./icons/stop.png'))
         self.playButton.setIcon(QtGui.QIcon('./icons/play.png'))

         # set model in tree view
         #self.build_file_system()

         # create music list from file system
         self.populate_song_list_from_fs()

         # create playlists list
         self.populate_playlist_list()

         # create context menu for the song list
         self.songsListWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
         self.songsListWidget.customContextMenuRequested.connect(self.onContext)

         # timer used to update the slider which shows the elapsed time of a song
         self.durationTimer = QTimer()
         self.durationTimer.timeout.connect(self.set_song_elapsed_time)
         self.durationTimer.start(1000)

         # Single shot timer used to parse all the playlist in background
         QTimer.singleShot(1000, self.parse_playlists_songs)

         # register a function that GLib will call every second
         #GLib.timeout_add_seconds(1, self.get_stream_duration)


     # Dinamically creates context menu according to playlist
     def onContext(self, position):
         # Create a menu
         menu = QtGui.QMenu("Menu", self)
         playlist_sub_menu = QtGui.QMenu("Add to playlist", self)
         #playlist_action =  QtGui.Action()

         for pl in self.playlists:
            # this will be executed for each playlist
            new_action = playlist_sub_menu.addAction(pl)
            receiver = lambda new_action=new_action: self.add_to_playlist(new_action)
            self.connect(new_action, SIGNAL('triggered()'), receiver)
            playlist_sub_menu.addAction(new_action)

         # add the sbubmenu to the menu
         menu.addMenu(playlist_sub_menu)
         # Show the context menu.
         menu.exec_(self.songsListWidget.mapToGlobal(position))


     def parse_playlists_songs(self):
        print "About to parse all the playlists.."
        self.playlists = self.playlist_manager.populate_playlists()
        print "Updated playlists info with all the songs"


     def add_to_playlist(self, action):
        # get the song to be added to the playlist
        song = self.songsListWidget.currentItem()
        print "Current song: {0} will be added to {1}".format(song.get_media_path(), action.iconText())

        # get data to add
        song_path = song.get_media_path()
        song_title = os.path.basename(song_path)
        playlist_name = str(action.iconText())
        # add to playlist
        self.playlists[playlist_name]["songs"].append(song_title)
        self.playlists[playlist_name]["paths"].append(song_path)

        print "Playlist {0} has {1} songs now".format(action.iconText(), len(self.playlists[playlist_name]["songs"]))


     def populate_songs_list(self):
         # clear the current songs
         self.songsListWidget.clear()

     # called when a pipeline is set to PLAYING.
     # Triggered by a signal from backend.py
     def set_song_elapsed_time(self):
         #self.player.get_song_duration()
         self.elapsedTimeSlider.setValue(self.player.get_song_elapsed())
         self.elapsedTimeSlider.setMaximum(self.player.get_song_duration())
         #print "Position: {0}".format(self.player.get_song_elapsed())
         #print "Duration: {0}".format(self.player.get_song_duration())


     # Called when elapsedTimeSlider has been released
     def seek_song_position(self):
         print "New value {0}".format(self.elapsedTimeSlider.value())
         self.player.seek_song_position(self.elapsedTimeSlider.value())


     '''def build_file_system(self):
         self.music_root = expanduser("~") + "/Music"
         self.fs_model = QtGui.QFileSystemModel(self)
         self.fs_model.setRootPath(self.music_root)
         self.indexRoot = self.fs_model.index(self.fs_model.rootPath())

         self.fileSystemView.setModel(self.fs_model)
         self.fileSystemView.setRootIndex(self.indexRoot)'''

     def populate_playlist_list(self):
         # get all the playlists
         self.playlists = self.playlist_manager.get_playlists()

         # populate the list# declare a playlist dictionary that will hold all the needed data with the custom object
         for playlist in self.playlists:
            playlist_name = playlist
            playlist_path = self.playlists[playlist]["playlist_path"]

            # create and populate a custom object
            customPlaylistObject = CustomPlaylistQWidget()
            #os.path.splitext(str(playlist))[0]
            #get the base name wo extension
            customPlaylistObject.set_playlist_name(playlist_name)
            customPlaylistObject.set_playlist_path(playlist_path)

            customQListWidgetItem = CustomQListPlaylistWidgetItem(
                                    customPlaylistObject.get_playlist_name(),
                                    customPlaylistObject.get_playlist_path())
            # Set size hint and media path
            customQListWidgetItem.setSizeHint(customPlaylistObject.sizeHint())

            # Add QListWidgetItem into QListWidget
            self.playlistListWidget.addItem(customQListWidgetItem)
            self.playlistListWidget.setItemWidget(customQListWidgetItem, customPlaylistObject)

            self.playlistListWidget.addItem(customQListWidgetItem)


     # Create the list of songs starting from the playlist object
     def create_playlist_songs_list(self, item):
         playlist_name =  item.get_playlist_name()

         # populate the list
         if self.playlists[playlist_name]["songs"]:
            # remove the current songs
            self.songsListWidget.clear()
            # create the list
            self.populate_song_list_from_playlist(
                      self.playlists[playlist_name]["songs"],
                      self.playlists[playlist_name]["paths"])
         else:
            print "No song in the playlist"

         #TODO: make 'populate_song_list' to handle generic lists


     # populate the songs list from a playlist file
     def populate_song_list_from_playlist(self, songs, paths):
         # loop over the songs in the playlist
         for i in range(0, len(songs)):
             # get the i-th item
             file_song = songs[i]
             full_path_file = paths[i]

             songCustomWidget = CustomQWidget()
             # TODO: properly extract artist name
             songCustomWidget.set_artist_name("Unknown")
             songCustomWidget.set_song_title(file_song)
             songCustomWidget.set_media_path(full_path_file)

             customQListWidgetItem = CustomQListWidgetItem(songCustomWidget.get_media_path()) #QtGui.QListWidgetItem(self.songsListWidget)
             # Set size hint and media path
             customQListWidgetItem.setSizeHint(songCustomWidget.sizeHint())

             # Add QListWidgetItem into QListWidget
             self.songsListWidget.addItem(customQListWidgetItem)
             self.songsListWidget.setItemWidget(customQListWidgetItem, songCustomWidget)



     def populate_song_list_from_fs(self):
         # set basic variable used to visit the filesystem
         home = expanduser("~")
         music_path = join(home, "Music/")

         for current_dir, subdirs, files in walk(music_path):
             for file_song in files:
                full_path_file = join(current_dir, file_song)
                if isfile(full_path_file) and file_song.endswith('.mp3'):
                   # Create a CustomQWidget for each item that must be added to the list
                   songCustomWidget = CustomQWidget()
                   # TODO: properly extract artist name
                   songCustomWidget.set_artist_name("Unknown")
                   songCustomWidget.set_song_title(file_song)
                   songCustomWidget.set_media_path(full_path_file)

                   customQListWidgetItem = CustomQListWidgetItem(songCustomWidget.get_media_path()) #QtGui.QListWidgetItem(self.songsListWidget)
                   # Set size hint and media path
                   customQListWidgetItem.setSizeHint(songCustomWidget.sizeHint())

                   # Add QListWidgetItem into QListWidget
                   self.songsListWidget.addItem(customQListWidgetItem)
                   self.songsListWidget.setItemWidget(customQListWidgetItem, songCustomWidget)



     def play_song(self, song):
         print "Selected {}".format(song.get_media_path())
         # Get the current index. It will be incremented later if needed
         self.currentSongIndex = self.songsListWidget.row(song)
         self.player.load_audio(song.get_media_path())
         self.playButton.setText('Pause')
         self.playButton.setIcon(QtGui.QIcon('./icons/pause.png'))


     def play_next_song(self):
         # used to select the next song
         self.currentSongIndex += 1
         self.next_song = self.songsListWidget.item(self.currentSongIndex)
         print "Next song {}".format(self.next_song.get_media_path())
         self.player.load_audio(self.next_song.get_media_path())
         self.songsListWidget.setCurrentRow(self.currentSongIndex)


     def playPauseAudio(self):
         self.player.play_pause_audio()
         if self.playButton.text() == 'Play':
             self.playButton.setText('Pause')
             self.playButton.setIcon(QtGui.QIcon('./icons/pause.png'))
         else:
             self.playButton.setText('Play')
             self.playButton.setIcon(QtGui.QIcon('./icons/play.png'))


     def stopAudio(self):
         self.player.stop_audio()
         self.playButton.setText('Play')
         self.playButton.setIcon(QtGui.QIcon('./icons/play.png'))


     def changeVolume(self):
        self.player.set_volume(float(self.volumeSlider.value())/100)


     def browseFs(self):
         filepath = QFileDialog.getOpenFileName(self, 'Choose File')
         if filepath:
             self.player.load_audio(str(filepath))
         else:
            print "Cannot load any song.."


if __name__ == '__main__':

     GObject.threads_init()
     qApp = QApplication(sys.argv)
     qApp.connect(qApp, SIGNAL('lastWindowClosed()'),
                  qApp, SLOT('quit()'))
     mainwindow = MainWindow()
     mainwindow.show()
     sys.exit(qApp.exec_())
