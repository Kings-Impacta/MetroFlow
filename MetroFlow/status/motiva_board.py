"""Última ocorrência por linha no quadro público oficial das linhas 8 e 9."""
from datetime import datetime
from html.parser import HTMLParser
import re
from .domain import LineCondition, situation
from .metro_board import BRASILIA

MOTIVA_URL = 'https://trilhos.motiva.com.br/viamobilidade8e9/situacao-das-linhas/'
VOID = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}


class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []

    def nodes(self):
        for child in self.children:
            if isinstance(child, Node):
                yield child
                yield from child.nodes()

    def text(self):
        return ' '.join(' '.join(child.text() if isinstance(child, Node) else child
                                 for child in self.children).split())

    def has_class(self, name):
        return name in self.attrs.get('class','').split()


class PublicTree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack)-1,0,-1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if not any(node.tag in {'script','style'} for node in self.stack):
            self.stack[-1].children.append(data)


def field(post, name):
    values = [node.text() for node in post.nodes() if node.has_class(name)]
    if len(values) != 1:
        raise ValueError('Campo ausente ou duplicado no quadro Motiva')
    return values[0]


def normalize_motiva_board(payload, now):
    if not isinstance(payload,str) or len(payload)>500000:
        raise ValueError('Quadro Motiva inválido')
    tree = PublicTree(); tree.feed(payload); tree.close()
    nodes = list(tree.root.nodes())
    tabs = {}
    for node in nodes:
        if node.attrs.get('role') != 'tab':
            continue
        match = re.fullmatch(r'([89])\s*-\s*(Diamante|Esmeralda)',node.text())
        if match:
            if match[2] != {'8':'Diamante','9':'Esmeralda'}[match[1]]:
                raise ValueError('Número e nome da linha Motiva incompatíveis')
            code = 'L'+match[1]
            key = node.attrs.get('id')
            if not key or key in tabs or code in tabs.values():
                raise ValueError('Abas Motiva ambíguas')
            tabs[key] = code
    if set(tabs.values()) != {'L8','L9'}:
        raise ValueError('Linhas Motiva ausentes')
    result = []
    for key, code in tabs.items():
        panels = [node for node in nodes if node.attrs.get('role')=='tabpanel'
                  and node.attrs.get('aria-labelledby')==key]
        if len(panels)!=1:
            raise ValueError('Painel Motiva ausente ou duplicado')
        posts = [node for node in panels[0].nodes() if node.has_class('block-post-list-container__post-item')]
        entries = []
        for post in posts:
            date = datetime.strptime(field(post,'post-time'),'%d/%m/%Y às %H:%M:%S').replace(tzinfo=BRASILIA).timestamp()
            label, description = field(post,'post-title'), field(post,'post-description')
            if not label or date>now+60:
                raise ValueError('Situação ou data Motiva inválida')
            entries.append((date,label,description))
        if not entries:
            raise ValueError('Nenhuma ocorrência Motiva')
        latest = max(date for date,_,_ in entries)
        choices = {(label,description) for date,label,description in entries if date==latest}
        if len(choices)!=1:
            raise ValueError('Ocorrências Motiva conflitantes')
        label, description = choices.pop()
        result.append(LineCondition(line_code=code,situation=situation(label),label=label[:120],
            description=description[:1200],source='Motiva — ViaMobilidade 8 e 9',source_url=MOTIVA_URL,
            collected_at=now,updated_at=latest,validity='current',
            attribution='Fonte: quadro oficial ViaMobilidade — Motiva; última ocorrência publicada'))
    return result
