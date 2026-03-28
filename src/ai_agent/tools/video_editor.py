"""
Video editor tool for video processing and editing.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

try:
    from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeVideoClip
    from moviepy.video.fx import all as vfx
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


class VideoAction(Enum):
    """Available video actions."""
    TRIM = "trim"
    MERGE = "merge"
    SPLIT = "split"
    RESIZE = "resize"
    CONVERT = "convert"
    EXTRACT_AUDIO = "extract_audio"
    ADD_SUBTITLE = "add_subtitle"
    SPEED_UP = "speed_up"
    SLOW_DOWN = "slow_down"
    ROTATE = "rotate"
    FLIP = "flip"
    CROP = "crop"
    GET_INFO = "get_info"
    THUMBNAIL = "thumbnail"


@dataclass
class VideoInfo:
    """Information about a video file."""
    path: str
    duration: float
    fps: float
    width: int
    height: int
    codec: str
    file_size: int


class VideoEditor:
    """
    Handles video editing operations.
    
    Features:
    - Trim and merge videos
    - Resize and convert formats
    - Extract audio
    - Apply effects (speed, rotate, flip)
    - Generate thumbnails
    - Video analysis
    """
    
    def __init__(self, output_dir: str = "./output"):
        """
        Initialize the Video Editor.
        
        Args:
            output_dir: Directory for output files
        """
        self.logger = logging.getLogger("VideoEditor")
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)
        
        if not HAS_MOVIEPY:
            self.logger.warning(
                "moviepy not installed. Video editing features will be limited. "
                "Install with: pip install moviepy"
            )
            
    def is_available(self) -> bool:
        """Check if video editing is available."""
        return HAS_MOVIEPY
        
    async def execute_action(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a video action.
        
        Args:
            action: The action to perform
            params: Parameters for the action
            
        Returns:
            Result of the action
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Video editing not available. Install moviepy."
            }
            
        if params is None:
            params = {}
            
        try:
            action_enum = VideoAction(action)
        except ValueError:
            return {
                "success": False,
                "error": f"Unknown action: {action}"
            }
            
        # Execute the action
        if action_enum == VideoAction.TRIM:
            return await self._trim(params)
        elif action_enum == VideoAction.MERGE:
            return await self._merge(params)
        elif action_enum == VideoAction.SPLIT:
            return await self._split(params)
        elif action_enum == VideoAction.RESIZE:
            return await self._resize(params)
        elif action_enum == VideoAction.CONVERT:
            return await self._convert(params)
        elif action_enum == VideoAction.EXTRACT_AUDIO:
            return await self._extract_audio(params)
        elif action_enum == VideoAction.ADD_SUBTITLE:
            return await self._add_subtitle(params)
        elif action_enum == VideoAction.SPEED_UP:
            return await self._speed_up(params)
        elif action_enum == VideoAction.SLOW_DOWN:
            return await self._slow_down(params)
        elif action_enum == VideoAction.ROTATE:
            return await self._rotate(params)
        elif action_enum == VideoAction.FLIP:
            return await self._flip(params)
        elif action_enum == VideoAction.CROP:
            return await self._crop(params)
        elif action_enum == VideoAction.GET_INFO:
            return await self._get_info(params)
        elif action_enum == VideoAction.THUMBNAIL:
            return await self._thumbnail(params)
        else:
            return {
                "success": False,
                "error": f"Action not implemented: {action}"
            }
            
    async def _trim(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Trim a video."""
        input_path = params.get("input", "")
        start_time = params.get("start", 0)
        end_time = params.get("end", None)
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"trimmed_{Path(input_path).name}")
            
        try:
            clip = VideoFileClip(input_path)
            
            if end_time is None:
                end_time = clip.duration
                
            trimmed = clip.subclip(start_time, end_time)
            trimmed.write_videofile(output_path, logger=None)
            
            clip.close()
            trimmed.close()
            
            return {
                "success": True,
                "action": "trim",
                "input": input_path,
                "output": output_path,
                "start": start_time,
                "end": end_time
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _merge(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge multiple videos."""
        input_paths = params.get("inputs", [])
        output_path = params.get("output", "")
        
        if not input_paths:
            return {"success": False, "error": "No input paths specified"}
            
        if not output_path:
            output_path = str(self._output_dir / "merged_video.mp4")
            
        try:
            clips = []
            for path in input_paths:
                clips.append(VideoFileClip(path))
                
            final_clip = concatenate_videoclips(clips)
            final_clip.write_videofile(output_path, logger=None)
            
            for clip in clips:
                clip.close()
            final_clip.close()
            
            return {
                "success": True,
                "action": "merge",
                "inputs": input_paths,
                "output": output_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _split(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Split a video into parts."""
        input_path = params.get("input", "")
        segment_duration = params.get("segment_duration", 60)
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        try:
            clip = VideoFileClip(input_path)
            duration = clip.duration
            
            segments = []
            start = 0
            segment_num = 1
            
            while start < duration:
                end = min(start + segment_duration, duration)
                segment = clip.subclip(start, end)
                
                output_path = str(self._output_dir / f"segment_{segment_num}_{Path(input_path).name}")
                segment.write_videofile(output_path, logger=None)
                
                segments.append({
                    "segment": segment_num,
                    "start": start,
                    "end": end,
                    "output": output_path
                })
                
                segment.close()
                start = end
                segment_num += 1
                
            clip.close()
            
            return {
                "success": True,
                "action": "split",
                "input": input_path,
                "segments": segments,
                "total_segments": len(segments)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _resize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Resize a video."""
        input_path = params.get("input", "")
        width = params.get("width", None)
        height = params.get("height", None)
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not width and not height:
            return {"success": False, "error": "Width or height required"}
            
        if not output_path:
            output_path = str(self._output_dir / f"resized_{Path(input_path).name}")
            
        try:
            clip = VideoFileClip(input_path)
            
            if width and height:
                resized = clip.resize((width, height))
            elif width:
                resized = clip.resize(width=width)
            else:
                resized = clip.resize(height=height)
                
            resized.write_videofile(output_path, logger=None)
            
            clip.close()
            resized.close()
            
            return {
                "success": True,
                "action": "resize",
                "input": input_path,
                "output": output_path,
                "width": width,
                "height": height
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _convert(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Convert video format."""
        input_path = params.get("input", "")
        output_format = params.get("format", "mp4")
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"{Path(input_path).stem}.{output_format}")
            
        try:
            clip = VideoFileClip(input_path)
            clip.write_videofile(output_path, logger=None)
            clip.close()
            
            return {
                "success": True,
                "action": "convert",
                "input": input_path,
                "output": output_path,
                "format": output_format
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _extract_audio(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract audio from video."""
        input_path = params.get("input", "")
        output_path = params.get("output", "")
        output_format = params.get("format", "mp3")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"{Path(input_path).stem}.{output_format}")
            
        try:
            clip = VideoFileClip(input_path)
            audio = clip.audio
            
            if audio is None:
                clip.close()
                return {"success": False, "error": "No audio track found"}
                
            audio.write_audiofile(output_path, logger=None)
            
            clip.close()
            audio.close()
            
            return {
                "success": True,
                "action": "extract_audio",
                "input": input_path,
                "output": output_path,
                "format": output_format
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _add_subtitle(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add subtitle to video."""
        input_path = params.get("input", "")
        subtitle_path = params.get("subtitle", "")
        output_path = params.get("output", "")
        
        if not input_path or not subtitle_path:
            return {"success": False, "error": "Input and subtitle paths required"}
            
        if not output_path:
            output_path = str(self._output_dir / f"subtitled_{Path(input_path).name}")
            
        try:
            from moviepy.video.tools.subtitles import SubtitlesClip
            
            clip = VideoFileClip(input_path)
            
            generator = lambda txt: TextClip(txt, font='Arial', fontsize=24, color='white')
            subtitles = SubtitlesClip(subtitle_path, generator)
            
            final = CompositeVideoClip([clip, subtitles.set_position(('center', 'bottom'))])
            final.write_videofile(output_path, logger=None)
            
            clip.close()
            final.close()
            
            return {
                "success": True,
                "action": "add_subtitle",
                "input": input_path,
                "subtitle": subtitle_path,
                "output": output_path
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _speed_up(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Speed up video."""
        input_path = params.get("input", "")
        speed_factor = params.get("factor", 2.0)
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"sped_up_{Path(input_path).name}")
            
        try:
            clip = VideoFileClip(input_path)
            sped_up = clip.speedx(speed_factor)
            sped_up.write_videofile(output_path, logger=None)
            
            clip.close()
            sped_up.close()
            
            return {
                "success": True,
                "action": "speed_up",
                "input": input_path,
                "output": output_path,
                "factor": speed_factor
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _slow_down(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Slow down video."""
        input_path = params.get("input", "")
        speed_factor = params.get("factor", 0.5)
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"slowed_down_{Path(input_path).name}")
            
        try:
            clip = VideoFileClip(input_path)
            slowed = clip.speedx(speed_factor)
            slowed.write_videofile(output_path, logger=None)
            
            clip.close()
            slowed.close()
            
            return {
                "success": True,
                "action": "slow_down",
                "input": input_path,
                "output": output_path,
                "factor": speed_factor
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _rotate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Rotate video."""
        input_path = params.get("input", "")
        angle = params.get("angle", 90)
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"rotated_{Path(input_path).name}")
            
        try:
            clip = VideoFileClip(input_path)
            rotated = clip.rotate(angle)
            rotated.write_videofile(output_path, logger=None)
            
            clip.close()
            rotated.close()
            
            return {
                "success": True,
                "action": "rotate",
                "input": input_path,
                "output": output_path,
                "angle": angle
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _flip(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Flip video."""
        input_path = params.get("input", "")
        direction = params.get("direction", "horizontal")
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"flipped_{Path(input_path).name}")
            
        try:
            clip = VideoFileClip(input_path)
            
            if direction == "horizontal":
                flipped = clip.fx(vfx.mirror_x)
            else:
                flipped = clip.fx(vfx.mirror_y)
                
            flipped.write_videofile(output_path, logger=None)
            
            clip.close()
            flipped.close()
            
            return {
                "success": True,
                "action": "flip",
                "input": input_path,
                "output": output_path,
                "direction": direction
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _crop(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Crop video."""
        input_path = params.get("input", "")
        x1 = params.get("x1", 0)
        y1 = params.get("y1", 0)
        x2 = params.get("x2", None)
        y2 = params.get("y2", None)
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"cropped_{Path(input_path).name}")
            
        try:
            clip = VideoFileClip(input_path)
            
            if x2 is None:
                x2 = clip.w
            if y2 is None:
                y2 = clip.h
                
            cropped = clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
            cropped.write_videofile(output_path, logger=None)
            
            clip.close()
            cropped.close()
            
            return {
                "success": True,
                "action": "crop",
                "input": input_path,
                "output": output_path,
                "region": {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _get_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get video information."""
        input_path = params.get("input", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        try:
            clip = VideoFileClip(input_path)
            
            info = {
                "path": input_path,
                "duration": clip.duration,
                "fps": clip.fps,
                "width": clip.w,
                "height": clip.h,
                "file_size": os.path.getsize(input_path)
            }
            
            clip.close()
            
            return {
                "success": True,
                "action": "get_info",
                "info": info
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
            
    async def _thumbnail(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate video thumbnail."""
        input_path = params.get("input", "")
        time = params.get("time", 0)
        output_path = params.get("output", "")
        
        if not input_path:
            return {"success": False, "error": "No input path specified"}
            
        if not output_path:
            output_path = str(self._output_dir / f"thumbnail_{Path(input_path).stem}.jpg")
            
        try:
            clip = VideoFileClip(input_path)
            frame = clip.get_frame(time)
            
            from PIL import Image
            img = Image.fromarray(frame)
            img.save(output_path)
            
            clip.close()
            
            return {
                "success": True,
                "action": "thumbnail",
                "input": input_path,
                "output": output_path,
                "time": time
            }
        except Exception as e:
            return {"success": False, "error": str(e)}