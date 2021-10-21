import re
from asyncio import wait_for, sleep, TimeoutError
from itertools import chain
from random import SystemRandom, choice
from typing import Optional, TYPE_CHECKING, Pattern, List, Tuple

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

    async def handler(self, message: NewMessage):
        timeout_error = self.service.cfg['request_timeout']
        try:
            await wait_for(super().handler(message), timeout=timeout_error)
        except TimeoutError:
            self.service.logger.error('Timeout error for message %s' %
                                      message.raw_text)
            raise VkSendErrorException

    async def is_triggered(self, message: NewMessage) -> bool:
        if self.trigger_word is None or message.raw_text is None:
            return False
        else:
            return self.trigger_word in message.raw_text

    async def _handler(self, message: NewMessage):
        try:
            content = await self.get_content(message)
            if isinstance(content, tuple):
                for one_message in content:
                    await self.service.api.send_message(
                        peer_id=message.peer_id,
                        message=one_message)
                    await sleep(1)
            elif isinstance(content, str):
                await self.service.api.send_message(
                    peer_id=message.peer_id,
                    message=content)
        except VKException as e:
            if e.code == ErrorCodes.URI_TOO_LONG.value:
                raise VkSendErrorException

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
        return 'тупо 20' if result == 20 else str(result)


class RaiseErrorMessageHandler(LinaNewMessageHandler):
    trigger_word = 'умри'

    async def get_content(self, message: NewMessage):
        raise VkSendErrorException


class RegexpDiceMessageHandler(LinaNewMessageHandler):
    pattern: Pattern[str] = re.compile(
        r'(^|[\d\s]+)[dдк](\d+)\s*([xх/*+-]\d+)?\s*(k([h|l])(\d*))?')

    async def is_triggered(self, message: NewMessage) -> bool:
        if message.raw_text is not None:
            result = self.pattern.search(message.raw_text) is not None
            return result
        else:
            raise VkSendErrorException

    @staticmethod
    def cast_amount(amount: str) -> int:
        amount = amount.strip()
        return int(amount) if amount != '' else 1

    async def get_dice_pool(self, dice: int, amount: int) -> List[int]:
        result = list()
        for i in range(amount * 2):
            result.append(self.get_dice(dice))
            await sleep(0)
        self.service.logger.info(result)
        SystemRandom().shuffle(result)
        return result[:amount]

    def get_dice(self, dice: int) -> int:
        result = SystemRandom().randint(1, dice)
        return result

    @staticmethod
    def get_khl(pool: List[int],
                high_low: str,
                high_low_count: int) -> Tuple[List[int], List[int]]:
        indexes = (sorted(range(len(pool)),
                          key=pool.__getitem__,
                          reverse=high_low == 'h'))[:high_low_count]
        keep = list()
        drop = list()
        for index, item in enumerate(pool):
            if index in indexes:
                keep.append(item)
            else:
                drop.append(item)
        return keep, drop

    @staticmethod
    def pool_to_str(pool: List[int]) -> str:
        return ' + '.join(map(str, pool))

    async def get_content(self, message: NewMessage):
        if message.raw_text is not None:
            parse_result = self.pattern.findall(message.raw_text)
            amount: int = self.cast_amount(parse_result[0][0])
            dice: int = int(parse_result[0][1])
            modifier: str = parse_result[0][2]
            khl = parse_result[0][4]
            try:
                khl_count = int(parse_result[0][5])
            except ValueError:
                khl_count = 1
            if amount < 1 or dice < 1:
                raise VkSendErrorException
            dice_pool: List[int] = await self.get_dice_pool(dice, amount)
            if khl and khl_count:
                pool_keep, pool_drop = self.get_khl(dice_pool, khl, khl_count)
                pool_result_int = sum(pool_keep)
                if not len(pool_drop):
                    pool_result_str = self.pool_to_str(pool_keep)
                else:
                    pool_result_str = f'{self.pool_to_str(pool_keep)} | ' \
                                      f'{self.pool_to_str(pool_drop)}'
            else:
                pool_result_str = self.pool_to_str(dice_pool)
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
                return 'тупо 20 %s %s' % (modifier,
                                          ('= %s' % throw_result)
                                          if modifier != '' else '')

            result = '(%s) %s = %s' % (pool_result_str,
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
        earl = range(51918, 51965)
        tabby = range(54129, 54150)

        cats_id = [cat for cat in chain(peachy_ids,
                                        rumka_ids,
                                        misti_ids,
                                        seth_ids,
                                        lovely_ids,
                                        pair_id,
                                        snow_id,
                                        earl,
                                        tabby)]
        return SystemRandom().choice(cats_id)


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
        return SystemRandom().choice(self.answers)


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
        'Да это все масонский заговор',
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
        'Это тыковка',
        'Чертовы комми',
        'Проклятые бюрократы'
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
        return SystemRandom().choice(self.guilty)


class WhoIsChosenMessageHandler(LinaNewMessageHandler):
    trigger_word = 'кто избран'
    conference_id_modifier = 2000000000

    async def get_content(self, message: NewMessage):
        if message.peer_id < self.conference_id_modifier:
            return 'Ты избран, здесь же больше никого нет'
        try:
            chosen_one = await self.service.api.get_conversation_members(
                message.peer_id)
            return '%s, ты избран!' % SystemRandom().choice(chosen_one)
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
            try:
                parse_result = self.pattern.findall(message.raw_text)
                _min, _max = map(lambda x: int(x), parse_result[0])
                if _min > _max:
                    _min, _max = _max, _min
                result = SystemRandom().randint(_min, _max)
                return 'от %s до %s: %s' % (_min, _max, result)
            except (IndexError, ValueError):
                return
        else:
            raise VkSendErrorException


class SayHelloMessageHandler(LinaNewMessageHandler):
    trigger_word = 'привет'
    hellos = ['Привет',
              'Здравствуйте',
              'Хай!',
              'Йоу!'
              ]
    unique_hellos = {164555054: [
        "Да прибудет с тобой великая сила спирта",
        "Query: Is there someone that you need killed?",
        "Heia! It's me Lina"]}

    async def get_content(self, message: NewMessage):
        if message.from_id == self.service.cfg['admin_id']:
            return 'Привет, мастер!'
        elif message.from_id in self.unique_hellos:
            return SystemRandom().choice(self.unique_hellos[message.from_id])
        else:
            return SystemRandom().choice(self.hellos)


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
            return SystemRandom().choice(self.friendzone)
        else:
            return 'А я тебя нет'


class AlternateMessageHandler(LinaNewMessageHandler):
    trigger_word = ' или '

    async def get_content(self, message: NewMessage):
        return SystemRandom().choice(
            self.maybe_clear_raw_text(message).split(' или '))

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
        if 99 < result <= 100:
            return 'Монетка взорвалась и убила тебя'
        if 96 < result <= 99:
            return 'Зависла в воздухе'
        elif 90 < result <= 96:
            return 'Встала на ребро'
        elif 45 < result <= 90:
            return 'Решка'
        else:
            return 'Орел'


class HelpMessageHandler(LinaNewMessageHandler):
    triggers = ('help', 'помощь')

    async def is_triggered(self, message: NewMessage) -> bool:
        if message.raw_text is not None:
            return any(keyword in message.raw_text
                       for keyword in self.triggers)
        else:
            return False

    async def get_content(self, message: NewMessage):
        return (
            'Бот реагирует на команды в двух случаях: \r\n'
            '1) Если у бота есть права администратора или право просматривать '
            'всю переписку - на сообщения начинающиеся со слова  "Бот", '
            '"Лина" \r\n'
            '2) в остальных случаях только на упоминания бота через @ или *'
            '\r\n\r\n '
            'ОСНОВНЫЕ КОМАНДЫ БОТА\r\n\r\n'
            '"XкY, XdY, XдY" - бросить дайс с Y '
            'гранями в количестве X (если вместо X пустое место, то бот '
            'автоматически принимает его за единицу) \r\n '
            'Пример: "Лина 3д6"\r\n '
            'Помимо обычного броска можно к броску прибавлять (+), '
            'отнимать (-), умножать (x - русская и английская раскладка), '
            'и делить (/) на определенный модификатор.\r\n'
            'БРОСКИ С ПРЕИМУЩЕСТВОМ И ПОМЕХОЙ:\r\n\r\n '
            'Чтобы выбрать наибольшее значение из нескольких кубов, '
            'можно добавить необязательную команду kh (keep high). \r\n'
            'Чтобы выбрать наименьшее значение, '
            'можно добавить kl (keep low) \r\n'
            'Пример: Лина 2d20 kh - стандартный бросок с преимуществом\r\n\r\n'
            'Можно выбирать несколько лучших или худших значений, '
            'для этого после kh/kl добавляется число\r\n'
            'Пример: Лина 5д6 kl3 - бросить 5d6 и выбрать три наименьших '
            'из них\r\n'
            'ВАЖНО: Если у броска есть модификатор, он должен быть применен '
            'раньше, чем kl/kh.\r\n '
            'Лина 2д20 +1 kh - будет работать. \r\n'
            'Лина 2д20 kh +1 - модификатор не будет учтен\r\n\r\n'
            'ДРУГИЕ КОМАНДЫ: \r\n\r\n'
            '"Дайс" - синоним для команды 1d20\r\n\r\n '
            '"Рандом от X до Y" - Лина случайным образом '
            'выбирает любое число в диапазоне от X до Y\r\n\r\n',
            '"Монетка" - Лина бросает монету, и выдает результат\r\n\r\n '
            '"Посты" - Лина придумывает любое оправдание отсутствия постов '
            'за вас!\r\n\r\n "Кто избран" (только при наличии прав админа) '
            '- Лина случайным образом выбирает пользователя из всех '
            'состоящих в беседе\r\n\r\n "Мяу" - Лина постит случайный '
            'стикер с котиком\r\n\r\n'
            '"Шар судьбы" - Лина постит случайный ответ из вариантов '
            'классического Magic 8 ball')


class WhatTheFuckMessageHandler(LinaNewMessageHandler):
    trigger_word = 'что за хуйн'

    async def get_content(self, message: NewMessage):
        return 'А я что? Я ничего'


class Magic8BallMessageHangler(LinaNewMessageHandler):
    trigger_word = 'шар судьбы'

    ball_answers = [
        'Бесспорно',
        'Предрешено',
        'Никаких сомнений',
        'Определенно да',
        'Можешь быть уверен в этом',
        'Мне кажется - «да»',
        'Вероятнее всего',
        'Хорошие перспективы',
        'Знаки говорят - «да»',
        'Да',
        'Пока не ясно, попробуй снова',
        'Спроси позже',
        'Лучше не рассказывать',
        'Сейчас нельзя предсказать',
        'Сконцентрируйся и спроси опять',
        'Даже не думай',
        'Мой ответ - «нет»',
        'По моим данным - «нет»',
        'Перспективы не очень хорошие',
        'Весьма сомнительно'
    ]

    async def get_content(self, message: NewMessage):
        return SystemRandom().choice(self.ball_answers)
