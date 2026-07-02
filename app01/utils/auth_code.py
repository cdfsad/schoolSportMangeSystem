"""
图片验证码生成(P0 安全改造)。

原实现使用 random 模块(Mersenne Twister,可预测),攻击者在获取足够输出后
可推测后续验证码。改为 secrets(CSPRNG,密码学安全随机数)。

仅验证码字符本身的安全是关键;干扰元素(颜色、位置)不影响安全,
但为保持一致性统一使用基于 secrets 的 _randint。
"""

import secrets

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def _randint(a, b):
    """密码学安全的随机整数,等价于 random.randint(a, b),返回 [a, b] 闭区间。"""
    return a + secrets.randbelow(b - a + 1)


def check_code(width=120, height=30, char_length=5, font_file='Monaco.ttf', font_size=28):
    code = []
    img = Image.new(mode='RGB', size=(width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img, mode='RGB')

    def rnd_char():
        """生成随机验证码字符(使用 CSPRNG,防预测)"""
        choices = [
            chr(_randint(65, 90)),  # A-Z
            str(_randint(0, 9)),  # 0-9
            chr(_randint(97, 122)),  # a-z
        ]
        return secrets.choice(choices)

    def rnd_color():
        return _randint(0, 255), _randint(10, 255), _randint(64, 255)

    # 写文字
    font = ImageFont.truetype(font_file, font_size)
    for i in range(char_length):
        char = rnd_char()
        code.append(char)
        h = _randint(0, 4)
        draw.text((i * width / char_length, h), char, font=font, fill=rnd_color())

    # 写干扰点
    for i in range(40):
        draw.point([_randint(0, width), _randint(0, height)], fill=rnd_color())

    # 写干扰圆圈
    for i in range(40):
        draw.point([_randint(0, width), _randint(0, height)], fill=rnd_color())
        x = _randint(0, width)
        y = _randint(0, height)
        draw.arc((x, y, x + 4, y + 4), 0, 90, fill=rnd_color())

    # 画干扰线
    for i in range(5):
        x1 = _randint(0, width)
        y1 = _randint(0, height)
        x2 = _randint(0, width)
        y2 = _randint(0, height)
        draw.line((x1, y1, x2, y2), fill=rnd_color())

    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, ''.join(code)
