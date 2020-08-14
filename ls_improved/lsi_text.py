import unicodedata

from .config import Config


config = Config()
class Text():
    def __init__(self, text, start_color):
        self.text, self.style = self._from_tag_text(text, start_color)

    def _from_tag_text(self, text, start_color):
        '''
        Parameters:
            text : String
            start_color : String
                start color tag
        
        Returns:
            text_string : String
            text_style : List[style]
                style : Dict
                    style.keys: [tag, start_pos, end_pos]
        '''
        text = [{'tag':start_color, 'text':text}]
        for tag in set(config.tag.values())-set([';ss;', ';se;', ';dw;']):
            new_text_list = [[t] for t in text]
            for i, t in enumerate(text):
                splited_text = t['text'].split(tag)
                if len(splited_text)==1:
                    new_text = [t]
                elif len(splited_text)>1:
                    t['text'] = splited_text[0]
                    new_text = [t]
                    for st in splited_text[1:]:
                        new_text += [{'tag':tag, 'text':st}]
                new_text_list[i] = new_text
            text = []
            for t in new_text_list:
                text += t
        text_string = ''
        text_style = []
        text_count = 0
        for t in text:
            text_string += t['text']
            text_style += [{'tag': t['tag'], 'start_pos': text_count, 'end_pos': text_count+len(t['text'])}]
            text_count += len(t['text'])
        text_style += [{'tag': ';end;', 'start_pos': text_count, 'end_pos': text_count}]
        return text_string, text_style
    
    def insert_text(self, text, pos):
        self.text = self.text[:pos] + text + self.text[pos:]
        for i in range(len(self.style)):
            if self.style[i]['end_pos']>=pos:
                if self.style[i]['start_pos']>=pos:
                    self.style[i]['start_pos'] += len(text)
                self.style[i]['end_pos'] += len(text)
        self._sort_style()

    def insert_style(self, color_tag, pos):
        for i, style in enumerate(self.style):
            if pos >= style['start_pos'] and style['end_pos'] >= pos:
                end_pos = style['end_pos']
                self.style[i]['end_pos'] = pos
                break
            else:
                end_pos = len(self.text)
        self.style += [{'tag': color_tag, 'start_pos': pos, 'end_pos': end_pos}]
        self._sort_style()

    def _search_end(self, index):
        color = ''
        for i, st in enumerate(self.style[:index-1]):
            if st['tag'] in [';ss;', ';se;', ';nl;', ';nle;']:
                pass
            else:
                color += config.color[st['tag']]
        return config.get_color('end')+color

    def _new_line_end(self, index):
        color = ''
        for i, st in enumerate(self.style[:index-1]):
            if st['tag'] in [';ss;', ';se;', ';nl;', ';nle;']:
                pass
            else:
                color += config.color[st['tag']]
        return config.get_color('end')+color
    
    def _sort_style(self):
        self.style.sort(key=lambda x: x['start_pos'])
        style = []
        tmp_style = []
        tmp_first_style = []
        tmp_last_style = []
        start_pos = 0
        end_pos = 0
        for i, st in enumerate(self.style):
            if start_pos==st['start_pos']:
                if st['end_pos']!=st['start_pos']:
                    end_pos = st['end_pos']
                    st['end_pos'] = st['start_pos']
                if st['tag'] in [';end;', ';e;', ';se;']:
                    tmp_first_style += [st]
                elif st['tag'] in [';nl;', ';nle;']:
                    tmp_last_style += [st]
                else:
                    tmp_style += [st]
            else:
                style += tmp_first_style + tmp_style + tmp_last_style
                style[-1]['end_pos'] = end_pos 
                if st['end_pos']!=st['start_pos']:
                    end_pos = st['end_pos']
                    st['end_pos'] = st['start_pos']
                if st['tag'] in [';end;', ';e;', ';se;']:
                    tmp_first_style = [st]
                    tmp_last_style = []
                    tmp_style = []
                elif st['tag'] in [';nl;', ';nle;']:
                    tmp_first_style = []
                    tmp_last_style = [st]
                    tmp_style = []
                else:
                    tmp_first_style = []
                    tmp_last_style = []
                    tmp_style = [st]
                if i == len(self.style)-1:
                    style += tmp_first_style + tmp_style + tmp_last_style
                    style[-1]['end_pos'] = end_pos
                start_pos = st['start_pos']
        self.style = style

    def __len__(self):
        def get_east_asian_width_count(text):
            count = 0
            for c in text:
                if unicodedata.east_asian_width(c) in 'FWA':
                    count += 2
                else:
                    count += 1
            return count
        return get_east_asian_width_count(self.text)

    def render(self):
        self._sort_style()
        text = ''
        for i, tag in enumerate(self.style):
            s = tag['start_pos']
            e = tag['end_pos']
            if tag['tag']==';se;':
                color = self._search_end(i)
            elif tag['tag']==';nle;':
                color = self._new_line_end(i)
            else:
                color = config.color[tag['tag']]
            text += color + self.text[s:e]
        return text + config.get_color('end')
