"""Prepare narration separately from canonical scripture and subtitles."""
import re

def omit_parentheses(text):
    stack=[];out=[]
    for char in text:
        if char in '（(':
            stack.append(char)
        elif char in '）)':
            if not stack:raise ValueError('Unmatched closing parenthesis')
            stack.pop()
        elif not stack:
            out.append(char)
    if stack:raise ValueError('Unmatched opening parenthesis')
    return ''.join(out)

def chinese_number(number):
    n=int(number);digits='零一二三四五六七八九'
    if n<10:return digits[n]
    if n<100:return (digits[n//10] if n>=20 else '')+'十'+(digits[n%10] if n%10 else '')
    raise ValueError('Chapter or verse outside supported range')

def speech_text(text):
    text=omit_parentheses(text)
    pattern=r'(?<!\d)(\d{1,2})\s*[:：]\s*(\d{1,2})(?:\s*[-–—~～]\s*(\d{1,2}))?(?!\d)'
    def reference(match):
        chapter,start,end=match.groups()
        return '第'+chinese_number(chapter)+'章'+chinese_number(start)+('到'+chinese_number(end) if end else '')+'节'
    text=re.sub(pattern,reference,text)
    # The Microsoft Edge endpoint escapes SSML. Use a same-sound character
    # only in the spoken input; canonical scripture and captions retain 差.
    text=re.sub(r'差(?=遣|派|来|我|他|你)', '拆', text)
    return text
