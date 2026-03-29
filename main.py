import io
from typing import Iterable

from astrbot.api import logger
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.message_components import Image, Reply
from astrbot.api.star import Context, Star, register
from PIL import Image as PILImage
from PIL import ImageSequence


HELP_TEXT = (
    "图像对称插件使用说明：\n"
    "1. 直接发送：指令 + 图片\n"
    "2. 回复处理：回复一条带图片的消息，再发送指令\n\n"
    "支持指令：\n"
    "- /对称、/对称左 或 /左对称：将左半部分镜像到右半部分\n"
    "- /对称右 或 /右对称：将右半部分镜像到左半部分\n"
    "- /对称上 或 /上对称：将上半部分镜像到下半部分\n"
    "- /对称下 或 /下对称：将下半部分镜像到上半部分"
)

COMMAND_TO_DIRECTION = {
    "对称": "left",
    "对称左": "left",
    "对称右": "right",
    "对称上": "top",
    "对称下": "bottom",
}


def _apply_symmetry(img_rgba: PILImage.Image, result_img: PILImage.Image, direction: str) -> None:
    width, height = img_rgba.size

    if direction == "left":
        mid_point = width // 2
        left_half = img_rgba.crop((0, 0, mid_point, height))
        mirrored_left = left_half.transpose(PILImage.FLIP_LEFT_RIGHT)
        result_img.paste(left_half, (0, 0), left_half)
        result_img.paste(mirrored_left, (mid_point, 0), mirrored_left)
    elif direction == "right":
        mid_point = width // 2
        right_half = img_rgba.crop((mid_point, 0, width, height))
        mirrored_right = right_half.transpose(PILImage.FLIP_LEFT_RIGHT)
        result_img.paste(right_half, (mid_point, 0), right_half)
        result_img.paste(mirrored_right, (0, 0), mirrored_right)
    elif direction == "top":
        mid_point = height // 2
        top_half = img_rgba.crop((0, 0, width, mid_point))
        mirrored_top = top_half.transpose(PILImage.FLIP_TOP_BOTTOM)
        result_img.paste(top_half, (0, 0), top_half)
        result_img.paste(mirrored_top, (0, mid_point), mirrored_top)
    elif direction == "bottom":
        mid_point = height // 2
        bottom_half = img_rgba.crop((0, mid_point, width, height))
        mirrored_bottom = bottom_half.transpose(PILImage.FLIP_TOP_BOTTOM)
        result_img.paste(bottom_half, (0, mid_point), bottom_half)
        result_img.paste(mirrored_bottom, (0, 0), mirrored_bottom)
    else:
        raise ValueError(f"unsupported direction: {direction}")


def _process_single_frame(frame: PILImage.Image, direction: str) -> PILImage.Image:
    img_rgba = frame.convert("RGBA")
    result_img = PILImage.new("RGBA", img_rgba.size, (0, 0, 0, 0))
    _apply_symmetry(img_rgba, result_img, direction)
    return result_img


def _save_static_image(img: PILImage.Image, original_format: str | None) -> bytes:
    output = io.BytesIO()
    image_format = (original_format or "PNG").upper()
    save_image = img

    if image_format in {"JPG", "JPEG"} and img.mode == "RGBA":
        background = PILImage.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        save_image = background
        image_format = "JPEG"

    save_image.save(output, format=image_format)
    return output.getvalue()


def _save_gif(frames: list[PILImage.Image], durations: list[int], original_img: PILImage.Image) -> bytes:
    output = io.BytesIO()
    processed_frames = [frame if frame.mode == "RGBA" else frame.convert("RGBA") for frame in frames]
    processed_frames[0].save(
        output,
        format="GIF",
        append_images=processed_frames[1:],
        save_all=True,
        duration=durations,
        loop=0,
        disposal=original_img.info.get("disposal", 2),
        optimize=False,
    )
    return output.getvalue()


def process_image_bytes(img_bytes: bytes, direction: str) -> bytes:
    with PILImage.open(io.BytesIO(img_bytes)) as img:
        original_format = img.format
        is_animated_gif = (
            (original_format or "").upper() == "GIF"
            and getattr(img, "is_animated", False)
        )

        if is_animated_gif:
            frames = []
            durations = []
            for frame in ImageSequence.Iterator(img):
                frames.append(_process_single_frame(frame, direction))
                durations.append(frame.info.get("duration", 100))
            return _save_gif(frames, durations, img)

        result_img = _process_single_frame(img, direction)
        try:
            return _save_static_image(result_img, original_format)
        finally:
            result_img.close()


async def _read_image_bytes(image_component: Image) -> bytes:
    image_path = await image_component.convert_to_file_path()
    with open(image_path, "rb") as file:
        return file.read()


def _iter_images(chain: Iterable[object]) -> Iterable[Image]:
    for component in chain:
        if isinstance(component, Image):
            yield component
        elif isinstance(component, Reply) and component.chain:
            for reply_component in component.chain:
                if isinstance(reply_component, Image):
                    yield reply_component


async def _extract_first_image_bytes(event: AstrMessageEvent) -> bytes | None:
    for image_component in _iter_images(event.get_messages()):
        try:
            return await _read_image_bytes(image_component)
        except Exception:
            logger.exception("读取图片失败")
    return None


@register(
    "astrbot_plugin_image_symmetry",
    "hacchiroku",
    "AstrBot 图像对称插件，支持左右上下四种镜像变换",
    "1.0.0",
)
class ImageSymmetryPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def _handle_symmetry(self, event: AstrMessageEvent, direction: str):
        img_bytes = await _extract_first_image_bytes(event)
        if not img_bytes:
            yield event.plain_result("请直接发送图片，或回复一条带图片的消息后再使用该指令。")
            return

        try:
            processed_bytes = process_image_bytes(img_bytes, direction)
        except Exception:
            logger.exception("图像对称处理失败")
            yield event.plain_result("图像处理失败，请重试。")
            return

        yield event.chain_result([Image.fromBytes(processed_bytes)])

    @filter.command("对称", alias={"对称左", "左对称"})
    async def symmetric_left(self, event: AstrMessageEvent):
        """将图片左半部分镜像到右半部分。"""
        async for result in self._handle_symmetry(event, COMMAND_TO_DIRECTION["对称"]):
            yield result

    @filter.command("对称右", alias={"右对称"})
    async def symmetric_right(self, event: AstrMessageEvent):
        """将图片右半部分镜像到左半部分。"""
        async for result in self._handle_symmetry(event, COMMAND_TO_DIRECTION["对称右"]):
            yield result

    @filter.command("对称上", alias={"上对称"})
    async def symmetric_top(self, event: AstrMessageEvent):
        """将图片上半部分镜像到下半部分。"""
        async for result in self._handle_symmetry(event, COMMAND_TO_DIRECTION["对称上"]):
            yield result

    @filter.command("对称下", alias={"下对称"})
    async def symmetric_bottom(self, event: AstrMessageEvent):
        """将图片下半部分镜像到上半部分。"""
        async for result in self._handle_symmetry(event, COMMAND_TO_DIRECTION["对称下"]):
            yield result

    @filter.command("对称帮助")
    async def symmetry_help(self, event: AstrMessageEvent):
        """查看图像对称插件帮助。"""
        yield event.plain_result(HELP_TEXT)
