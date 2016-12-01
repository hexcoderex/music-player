import pygst
pygst.require('0.10')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import Screen

import os

# module to handle audio files
from music_player import MusicPlayer
from radio import RadioPlayer
from library_manager import LibraryManager

# class used to show a file system manager to choose a song to play
'''class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)'''

# class MusicScreen(Screen):
#     pass

class RadioScreen(Screen):
    def __init__(self, **kwargs):
       super(RadioScreen, self).__init__(**kwargs)
       self.radio_player = RadioPlayer()
       print "Radio Screen created"

    def play_station(self, radio):
      self.radio_player.stop_any_station()
      print "Station that must be played: {}".format(radio)
      self.radio_player.play_station(radio)


class MainGui(FloatLayout):

    # ScreenManager that will be used to change between the two screens
    sm = ObjectProperty()
   
    ''' Shows the popup to choose the file to play
    '''
    '''def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def dismiss_popup(self):
        self._popup.dismiss()'''

    def __init__(self, **kwargs):
       super(MainGui, self).__init__(**kwargs)
       self.library_manager = LibraryManager()
       self.player = MusicPlayer()
       library_text = self.ids.t_music_library
       # adding files to library
       songs = self.library_manager.parse_library()
       songs_text = ''
       for song in songs:
           songs_text = songs_text + song

       library_text.text = songs_text#''.join('aaaa ').join('bbbb')#, 'and something else')
       #library_text.text = library_text.text.join('bbbb')

       # Just prepare the screen manager
       #self.sm.add_widget(MusicScreen(name='MusicScreen'))
       self.sm.add_widget(RadioScreen(name='RadioScreen'))

    def switch_screen(self, args):
      self.sm.current = "{}Screen".format(args[1])
      print "Switching to '{}' screen...".format(args[1])

    def load(self, path, filename):
        #self.player.stop_audio()
        self.player.load_audio(filename[0])
        #self.dismiss_popup()

      
    '''Playing or pausing a song.
        1) If stopped play it again from the 'elapsed' value.
           If it's 0 play it from the beginning.
        2) If it's playing store the elapsed time and stop the song.
    '''
    def play_pause_audio(self):
      self.player.play_pause_audio()


    def pause_audio(self):
       self.player.pause_audio()       


    def play_audio(self):
       self.player.play_audio()
       # TODO: to be fully tested
       #self.player.look_bus()

    ''' Stopping the song.
        1) self.elapsed set to 0 so the next song (or the same)
           will be played from the beginning
        2) actually stop the song
    '''    
    def stop_audio(self):
       self.player.stop_audio()
 
    ''' Reloading the song if it's currently playing.
        Just call self.stop_song and then self.play_pause_song        
    '''
    def reload_audio(self):
       self.player.reload_audio()

    ''' Setting the volume.
        When the value of the slider is changed, this will affect the 
        volume of the played song.
    '''
    def set_volume(self, value):
       self.player.set_volume(value)


class TestApp(App):
    def build(self):
        return MainGui()

Factory.register('TestApp', cls=TestApp)
#Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == "__main__":
    TestApp().run()
