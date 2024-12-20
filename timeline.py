import numpy as np
import pygame
from config import *

class Timeline:
    def __init__(self) -> None:
        self.offset_x = 0
        self.track_height = 57
        self.unit_width = 50  # Pixel width per second
        self.track_count = 11
        self.dynamic_length = 100
        self.min_zoom = 40
        self.max_zoom = 400
        self.cursor_position = 0 
        self.is_playing = False  # Cursor movement active or not
        self.is_recording = False  
        self.recording_buffer = None  # Buffer for temp track
        self.active_track = None  # Recording track
        self.track_starts = [0] * self.track_count  # Tracks starting position
        self.waveform_cache = [None] * self.track_count

    def handleScroll(self, event):
        if pygame.key.get_pressed()[pygame.K_LCTRL] or pygame.key.get_pressed()[pygame.K_RCTRL]:
            if event.type == pygame.MOUSEWHEEL:
                zoom_change = 10
                cursor_time = self.cursor_position / self.unit_width
                
                old_unit_width = self.unit_width
                
                if event.y == -1 and self.unit_width - zoom_change >= self.min_zoom:
                    self.unit_width -= zoom_change
                elif event.y == 1 and self.unit_width + zoom_change <= self.max_zoom:
                    self.unit_width += zoom_change
                
                scale_factor = self.unit_width / old_unit_width
                self.track_starts = [int(start * scale_factor) for start in self.track_starts]
                
                self.cursor_position = cursor_time * self.unit_width
                
                total_length_px = self.dynamic_length * self.unit_width
                max_visible_x = self.offset_x + pygame.display.get_window_size()[0]
                if total_length_px < max_visible_x:
                    self.offset_x = max(0, self.offset_x - (max_visible_x - total_length_px))
                self.reset_waveform_cache()
        else:
            if event.type == pygame.MOUSEWHEEL:
                if event.y == 1:
                    self.offset_x += 100
                elif event.y == -1:
                    self.offset_x -= 100
                    if self.offset_x < 0:
                        self.offset_x = 0

    def handleClick(self, event, timeline_x, timeline_y, timeline_width, timeline_height, audio_manager):
        """
        Handles mouse clicks on the timeline. Left click moves the cursor.
        Right click deletes the clicked track.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos

            # Check if clicking is in timeline area.
            if timeline_x <= mouse_x <= timeline_x + timeline_width and timeline_y <= mouse_y <= timeline_y + timeline_height:
                # Left click moves cursor.
                if event.button == 1:
                    self.cursor_position = mouse_x + self.offset_x - timeline_x
                
                # Right click deletes track.
                elif event.button == 3:
                    track_index = (mouse_y - 70) // self.track_height  # Calculate track index.
                    if 0 <= track_index < self.track_count:
                        if audio_manager.tracks[track_index] is not None:
                            audio_manager.delete_track(track_index)

    def drawTimeline(self, win, x, y, width, height, tracks, sample_rate, wincolor, linecolor, temptrackcolor, trackcolor, wavecolor, theme):
        """
        Draws timeline and corresponding tracks.
        """
        wavecolor = theme[1]
        total_length_px = self.dynamic_length * self.unit_width
        self.autoExtendTimeline(win)
        
        timeline_surface = pygame.Surface((width, height))
        timeline_surface.fill(wincolor)

        font = pygame.font.SysFont("Arial", 20)        
        
        if self.is_recording and self.recording_buffer and self.active_track is not None:
            track_y = 26 + self.active_track * self.track_height
            pygame.draw.rect(
                timeline_surface, (temptrackcolor), 
                (
                    self.recording_buffer[0] - self.offset_x, track_y + 1,
                    self.recording_buffer[1] - self.recording_buffer[0], self.track_height
                )
            )

        for i, track in enumerate(tracks):
            track_y = 26 + i * (self.track_height)
            if track is not None:
                track_duration = len(track) / sample_rate
                track_width = int(track_duration * self.unit_width)

                track_x_start = self.track_starts[i] - self.offset_x

                pygame.draw.rect(
                    timeline_surface, (trackcolor), 
                    (track_x_start + 1, track_y+1, track_width, self.track_height)
                )

                if self.waveform_cache[i] is None:
                    self.waveform_cache[i] = self.generate_waveform_surface(track, track_width, self.track_height, wavecolor)

                if self.waveform_cache[i] is not None:
                    timeline_surface.blit(self.waveform_cache[i], (track_x_start, track_y))

            if i < len(tracks) - 1:
                line_y = track_y + self.track_height
                pygame.draw.line(timeline_surface, linecolor, (0, line_y), (width, line_y), 1)

        for col in range(0, int(total_length_px), int(self.unit_width)):
            pos_x = col - self.offset_x
            if 0 <= pos_x <= width:
                pygame.draw.line(timeline_surface, linecolor, (pos_x, 0), (pos_x, height))
                pygame.draw.line(timeline_surface, linecolor, (0, 26), (pos_x + 300, 26)) 
                text = font.render(str(col // self.unit_width + 1), True, "white")
                text_rect = text.get_rect(topleft=(pos_x+1, 5))
                timeline_surface.blit(text, text_rect)

        self.draw_cursor(timeline_surface, width, height, color="red")

        win.blit(timeline_surface, (x, y))

    def autoExtendTimeline(self, win):
        """
        Extend timeline.
        """
        screen_width = win.get_width()
        visible_end = self.dynamic_length * self.unit_width - self.offset_x
        if visible_end < screen_width + self.unit_width * 10:
            self.dynamic_length += 10

    def draw_cursor(self, surface, width, height, color="red"):
        """
        Draw cursor on timeline.
        """
        cursor_x = self.cursor_position - self.offset_x
        if 0 <= cursor_x <= width:
            pygame.draw.line(surface, color, (cursor_x, 0), (cursor_x, height), 2)

    def update_cursor(self, delta_time):
        """
        Updates cursor's position and ensures the timeline scrolls smoothly to keep the cursor visible.
        """
        if self.is_playing:
            # Cursor movement
            self.cursor_position += delta_time * self.unit_width
            self.cursor_position %= (self.dynamic_length * self.unit_width)

            if self.is_recording:
                if self.recording_buffer is None:
                    self.recording_buffer = [self.cursor_position, self.cursor_position]
                else:
                    self.recording_buffer[1] = self.cursor_position

            # Check if cursor is near timeline's range
            screen_width = pygame.display.get_window_size()[0]
            visible_end = self.offset_x + screen_width

            if self.cursor_position > visible_end - (screen_width * 0.2):
                self.offset_x += (self.cursor_position - visible_end + (screen_width * 0.2)) * 0.1  # Smooth scroll

            self.offset_x = max(0, self.offset_x)


    def start_timeline_recording(self, track_index):
        """Starts recording in timeline."""
        self.is_recording = True
        self.is_playing = True
        self.recording_buffer = None
        self.active_track = track_index
        self.track_starts[track_index] = self.cursor_position

    def stop_timeline_recording(self):
        """Stops recording in timeline."""
        self.is_recording = False
        self.is_playing = False
        self.recording_buffer = None
        self.active_track = None

    def reset_timeline(self):
        """
        Resets the timeline and cursor to the starting position.
        """
        self.cursor_position = 0
        self.offset_x = 0
        self.is_playing = False
        self.is_recording = False
        self.reset_waveform_cache()


    def generate_waveform_surface(self, track, width, height, color):
        """
        Generates a cached waveform surface for the given track.
        """
        if track is None or len(track) == 0:
            return None

        # Waveform normalization
        waveform = track / np.max(np.abs(track))
        samples_per_pixel = max(1, len(waveform) // width)
        reduced_waveform = [
            (np.min(waveform[i:i+samples_per_pixel]), np.max(waveform[i:i+samples_per_pixel]))
            for i in range(0, len(waveform), samples_per_pixel)
        ]

        waveform_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        waveform_surface.fill((0, 0, 0, 0))
        mid_y = height // 2
        for i, (min_val, max_val) in enumerate(reduced_waveform):
            pos_x = i
            top_y = mid_y - int(max_val * (height // 2))
            bottom_y = mid_y - int(min_val * (height // 2))
            pygame.draw.line(waveform_surface, color, (pos_x, top_y), (pos_x, bottom_y))

        return waveform_surface

    def reset_waveform_cache(self, track_index=None):
        """
        Resets waveform cache for all or a specific track.
        """
        if track_index is not None:
            self.waveform_cache[track_index] = None
        else:
            self.waveform_cache = [None] * self.track_count