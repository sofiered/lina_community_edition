import re

from itertools import chain
from random import SystemRandom, choice
from typing import Optional, TYPE_CHECKING, Pattern

from lina_community_version.core.handlers import BaseMessageHandler
from lina_community_version.core.messages import NewMessage
from lina_community_version.core.exceptions import VkSendErrorException, \
    VKException, ErrorCodes

if TYPE_CHECKING:
    from lina_community_version.lina.bot import Lina


class LinaNewMessageHandler(BaseMessageHandler):
    def __init__(self, service: 'Lina') -> None:
        self.service = service

    trigger_word: Optional[str] = None

    async def is_triggered(self, message: NewMessage) -> bool:
        if self.trigger_word is None or message.raw_text is None:
            return False
        else:
            return self.trigger_word in message.raw_text

    async def _handler(self, message: NewMessage):
        await self.service.api.send_message(
            peer_id=message.peer_id,
            message=await self.get_content(message))

    async def get_content(self, message: NewMessage):
        raise NotImplementedError


class PingPongMessageHandler(LinaNewMessageHandler):
    trigger_word = 'ping'

    async def get_content(self, message: NewMessage):
        return 'pong'


class SimpleDiceMessageHandler(LinaNewMessageHandler):
    trigger_word = 'дайс'

    async def get_content(self, _message: NewMessage):
        result = SystemRandom().randint(1, 20)
        return 'тупо 20' if result == 20 else result


class RaiseErrorMessageHandler(LinaNewMessageHandler):
    trigger_word = 'умри'

    async def get_content(self, message: NewMessage):
        raise VkSendErrorException


class RegexpDiceMessageHandler(LinaNewMessageHandler):
    pattern: Pattern[str] = re.compile(r'(\d+)[dдк](\d+)\s*([xх/*+-]\d+)?')

    async def is_triggered(self, message: NewMessage) -> bool:
        if message.raw_text is not None:
            return self.pattern.search(message.raw_text) is not None
        else:
            raise VkSendErrorException

    async def get_content(self, message: NewMessage):
        if message.raw_text is not None:
            parse_result = self.pattern.findall(message.raw_text)
            amount: int = int(parse_result[0][0])
            dice: int = int(parse_result[0][1])
            modifier: str = parse_result[0][2]

            if amount + dice > 1000:
                raise VkSendErrorException
            if amount < 1:
                raise VkSendErrorException
            if dice < 1:
                raise VkSendErrorException
            dice_pool = [SystemRandom().randint(1, dice)
                         # if not (self.bot.is_cheating
                         # and 'ч' in message.raw_text)
                         # else dice
                         for _ in range(amount)]
            pool_result_str = ' + '.join(map(str, dice_pool))
            pool_result_int = sum(dice_pool)
            number_modifier = int(modifier[1:]) if modifier != '' else 0
            if modifier.startswith('+'):
                throw_result = str(pool_result_int + number_modifier)
            elif modifier.startswith('-'):
                throw_result = str(pool_result_int - number_modifier)
            elif modifier.startswith('/'):
                throw_result = format(pool_result_int / number_modifier, '.2f')
            elif modifier.startswith(('x', 'х', '*')):
                throw_result = str(pool_result_int * number_modifier)
            else:
                throw_result = str(pool_result_int)

            if amount == 1 and dice == 20 and pool_result_int == 20:
                return 'тупо 20' + modifier

            result = '(%s)%s = %s' % (pool_result_str,
                                      modifier,
                                      throw_result)
            return result
        else:
            raise VkSendErrorException


class MeowMessageHandler(LinaNewMessageHandler):
    trigger_word = 'мяу'

    async def _handler(self, message: NewMessage):
        await self.service.api.send_sticker(
            peer_id=message.peer_id,
            sticker_id=await self.get_content(message))

    async def get_content(self, message: NewMessage):
        peachy_ids = range(49, 97)
        rumka_ids = range(5582, 5630)
        misti_ids = range(5701, 5745)
        seth_ids = range(6109, 6156)
        lovely_ids = range(7096, 7143)
        pair_id = range(11607, 11654)
        snow_id = range(11238, 11285)

        cats_id = [cat for cat in chain(peachy_ids,
                                        rumka_ids,
                                        misti_ids,
                                        seth_ids,
                                        lovely_ids,
                                        pair_id,
                                        snow_id)]
        return choice(cats_id)


class WhereArePostsMessageHandler(LinaNewMessageHandler):
    trigger_word = 'посты'
    answers = [
        'Сегодня будет, но позже',
        'Я уже пишу',
        'Вечером',
        'Я хз, что писать',
        'Вдохновения нет((('
    ]

    async def get_content(self, message: NewMessage):
        return choice(self.answers)


class InfoMessageHandler(LinaNewMessageHandler):
    trigger_word = 'инфа'

    async def get_content(self, message: NewMessage):
        info = SystemRandom().randint(1, 101)
        if info == 100:
            return 'инфа сотка'
        elif info == 101:
            return 'инфа 146%'
        else:
            return 'инфа %s%%' % info


class WhoIsGuiltyMessageHandler(LinaNewMessageHandler):
    trigger_word = 'кто виноват'
    guilty = [
        'Да это все массонский заговор',
        'Путин, кто же еще',
        'Это происки сатаны',
        'Рептилоиды, они же управляют всей планетой',
        'Судьба...',
        'Не знаю, но точно не я!',
        'Это все я, прости',
        'Глобальное потепление',
        'Ты сам. А кто же еще?',
        'Телевизор',
        'Интернет',
        'Тупые школьники',
        'Тыковка не виновата',
        'Это все хозяин',
        'Это тыковка'
    ]

    async def get_content(self, message: NewMessage):
        if SystemRandom().randint(1, 10) == 1:
            try:
                maybe_guilty = await self.service.api.get_conversation_members(
                    message.peer_id)
                return 'Это %s во всем виноват' % choice(maybe_guilty)
            except VKException as e:
                if e.code == ErrorCodes.ADMIN_PERMISSION_REQUIRED.value:
                    self.service.logger.warn(
                        'code %s, Admin permissions required!' % e.code)
                else:
                    raise e
        return choice(self.guilty)


class WhoIsChosenMessageHandler(LinaNewMessageHandler):
    trigger_word = 'кто избран'
    conference_id_modifier = 2000000000

    async def get_content(self, message: NewMessage):
        if message.peer_id < self.conference_id_modifier:
            return 'Ты избран, здесь же больше никого нет'
        try:
            chosen_one = await self.service.api.get_conversation_members(
                message.peer_id)
            return '%s, ты избран!' % choice(chosen_one)
        except VKException as e:
            self.service.logger.error(e)
            if e.code == ErrorCodes.ADMIN_PERMISSION_REQUIRED.value:
                return 'Для доступа к списку участников беседы ' \
                       'мне нужны админские права'


class IntervalRandomMessageHandler(LinaNewMessageHandler):
    trigger_word = 'рандом'
    pattern: Pattern[str] = re.compile(r'от\s*(\d+)\s*до\s*(\d+)?')

    async def get_content(self, message: NewMessage):
        if message.raw_text is not None:
            parse_result = self.pattern.findall(message.raw_text)
            _min, _max = map(lambda x: int(x), parse_result[0])
            if _min > _max:
                _min, _max = _max, _min
            result = SystemRandom().randint(_min, _max)
            return 'от %s до %s: %s' % (_min, _max, result)
        else:
            raise VkSendErrorException


class SayHelloMessageHandler(LinaNewMessageHandler):
    trigger_word = 'привет'
    hellos = ['Привет',
              'Здравствуйте',
              'Хай!',
              'Йоу!'
              ]

    async def get_content(self, message: NewMessage):
        return 'Привет, мастер!' \
            if message.from_id == self.service.cfg['admin_id'] \
            else choice(self.hellos)


class LoveYouMessageHandler(LinaNewMessageHandler):
    triggers = ('люблю тебя', 'я тебя люблю')
    friendzone = ['Ты мне как брат',
                  'Я тоже тебя люблю, как брата',
                  'Ты очень хороший друг']

    async def is_triggered(self, message: NewMessage) -> bool:
        if message.raw_text is not None:
            return any(keyword in message.raw_text
                       for keyword in self.triggers)
        else:
            return False

    async def get_content(self, message: NewMessage):
        if message.from_id == self.service.cfg['admin_id']:
            return 'Я тоже тебя люблю <3'
        elif message.from_id in self.service.cfg['friend_zone']:
            return choice(self.friendzone)
        else:
            return 'А я тебя нет'


class AlternateMessageHandler(LinaNewMessageHandler):
    trigger_word = ' или '

    async def get_content(self, message: NewMessage):
        return choice(self.maybe_clear_raw_text(message).split(' или '))

    @staticmethod
    def maybe_clear_raw_text(message: NewMessage) -> str:
        if message.raw_text is not None:
            if message.raw_text.endswith(('!', '.', '?')):
                return message.raw_text[:-1]
            else:
                return message.raw_text
        else:
            return ''


class CoinMessageHandler(LinaNewMessageHandler):
    trigger_word = 'монетка'

    async def get_content(self, message: NewMessage):
        result = SystemRandom().randint(1, 100)
        if 97 < result <= 100:
            return 'Зависла в воздухе'
        elif 90 < result <= 97:
            return 'Встала на ребро'
        elif 45 < result <= 90:
            return 'Решка'
        else:
            return 'Орел'
