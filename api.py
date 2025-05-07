import aiohttp
import asyncio
import json

import config

async def request(token, suburl, data):
    url = f"https://api.telegram.org/bot{token}/{suburl}"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()

async def get_stars(token, mamont):
    try:
        if mamont is None:
            return "Arguments exception"
        
        data = {
            'business_connection_id': str(mamont)
        }
        
        get = await request(token, "getBusinessAccountStarBalance", data)
        return get
    except Exception as e:
        return f"Failed to create request: {str(e)}"

async def get_gifts(token, mamont):
    try:
        if mamont is None:
            return "Arguments exception"
        
        data = {
            'business_connection_id': str(mamont)
        }
        
        get = await request(token, "getBusinessAccountGifts", data)
        return get
    except Exception as e:
        return f"Failed to create request: {str(e)}"

async def get_gift_list(token, mamont):
    try:
        _GIFTS = await get_gifts(token, mamont)
        if str(_GIFTS) == "Arguments exception" or str(_GIFTS).startswith("Failed to create request"):
            return [f"{_GIFTS}"]
        
        if not _GIFTS['ok']:
            desc = _GIFTS['description']
            return [f'Failed to recive gifts list: {desc}']
        
        _RESULT = _GIFTS['result']
        _COUNT = _RESULT['total_count']
        _NFT_COUNT = 0
        
        _GIFT_LIST = _RESULT['gifts']
        
        decoded_gifts = []
        for gift in _GIFT_LIST:
            if gift['type'] != "unique":
                continue
            
            gift_name = gift['gift']['name']
            decoded_gift = {
                'id': gift['owned_gift_id'],
                'name': f'{gift_name}'
            }
            
            _NFT_COUNT += 1
            decoded_gifts.append(decoded_gift)
            
        if _NFT_COUNT == 0 or _COUNT == 0:
            return ['User doesn`t have nft gifts']
        
        return [str(_NFT_COUNT), decoded_gifts]
    except Exception as ex:
        return [f'Failed: {str(ex)}']

async def transfer_gift(token, mamont, gift, transfer_to, star_count=25):
    try:
        if mamont is None or gift is None or transfer_to is None or star_count < 0 or star_count > 1000:
            return "Arguments exception"
        
        data = {
            'business_connection_id': str(mamont),
            'owned_gift_id': str(gift),
            'new_owner_chat_id': int(transfer_to),
            'star_count': star_count
        }
        
        get = await request(token, "transferGift", data)
        if not get['ok']:
            if str(get['description']).__contains__("NO_PAYMENT_NEEDED"):
                return await transfer_gift(token, mamont, gift, transfer_to, star_count=0)
        
        return get
    except Exception as e:
        return f"Failed to create request: {str(e)}"