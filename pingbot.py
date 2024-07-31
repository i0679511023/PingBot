import subprocess
from telegram import Bot
import asyncio

async def check_host_availability(host):
    result = subprocess.run(["ping", "-c", "1", host],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

async def send_telegram_notification(bot, chat_id, message):
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    except Exception as e:
        print(f"Ошибка отправки сообщения в Telegram: {e}")

async def main():
    previous_statuses = {}  # Добавим объявление переменной

    with open('vars.txt', 'r') as vars_file:
        for line in vars_file:
            key, value = line.strip().split('=')
            if key == 'TOKEN':
                TOKEN = value
            elif key == 'chat_id':
                chat_id = int(value)

    bot = Bot(TOKEN)

    start_message = "Начало проверки работы интернета в магазинах:"
    await send_telegram_notification(bot, chat_id, start_message)



    hosts = []
    with open('fajno_host.txt', 'r') as host_file:
        for line in host_file:
            host_info = line.strip().split()
            if len(host_info) >= 2:
                hosts.append((host_info[0], host_info[1]))

    for ip_address, host_name in hosts:
        current_status = "Интернет ЕСТЬ" if await check_host_availability(ip_address) else "Проблема!"

        if current_status == "Проблема!":
            message = f"{host_name}: {current_status}"
            await send_telegram_notification(bot, chat_id, message)

        previous_statuses[ip_address] = current_status

    while True:
        for ip_address, host_name in hosts:
            current_status = "Интернет ЕСТЬ" if await check_host_availability(ip_address) else "Проблема!"

            if ip_address in previous_statuses and previous_statuses[ip_address] != current_status:
                message = f"{host_name}: Статус изменился: {previous_statuses[ip_address]} ===> {current_status}"
                await send_telegram_notification(bot, chat_id, message)

            previous_statuses[ip_address] = current_status

        await asyncio.sleep(1800)

if __name__ == "__main__":
    asyncio.run(main())



