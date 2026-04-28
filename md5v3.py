import os
import telebot
from telebot import types
from datetime import datetime, timedelta
import json
import math
import numpy as np
import re
import hashlib
from collections import defaultdict
import time
import random
import asyncio

# ==============================================
# CẤU HÌNH HỆ THỐNG
# ==============================================
TOKEN = "8264938566:AAFWV0xp8nlTPbQ08skFD5I1srdNe_SRjw"
if not TOKEN:     raise ValueError("❌ BOT_TOKEN chưa được thiết lập.")
ADMIN_ID = 7071414779
LIEN_HE_HO_TRO = "@NguyenTung1920"
NHOM_YEU_CAU = ["https://t.me/+pxXrNnB-ciZmZWE1", "https://t.me/+MsSL6BSqpyRkZDJl" ,"https://t.me/tinnongv5" ,"https://t.me/shareallv2"]
MA_VIP = "VIP7NGAYMIENPHI"
TEN_BOT = "botmd5v2pro_bot"

bot = telebot.TeleBot(TOKEN)

# Biểu tượng cảm xúc cho phản hồi động
BIEU_TUONG_PHAN_HOI = ["🌌", "🚀", "🪐", "⭐", "💫"]

# Biểu tượng cho giao diện sống động
BIEU_TUONG_TRA_LOI = ["🌌", "🚀", "🪐", "⭐", "💫", "🌠", "🛸", "🔭", "🪐", "🌍"]

# Biểu tượng hệ thống cho giao diện hiện đại
BIEU_TUONG = {
    "thanh_cong": "✅", "loi": "❌", "thong_tin": "ℹ️", "canh_bao": "⚠️", "vip": "💎",
    "khoa": "🔒", "mo_khoa": "🔓", "dong_ho": "⏳", "thong_ke": "📈", "lich_su": "📜",
    "nguoi_dung": "👤", "quan_tri": "🛡️", "phat_tin": "📡", "moi_ban": "📨", "nhom": "👥",
    "tai": "🎰", "xiu": "🎲", "dong_co": "⚙️", "rủi_ro": "🚨", "thoi_gian": "⏰",
    "dung": "✔️", "sai": "❌", "phan_tich": "🔍", "moi": "📩", "tro_giup": "🆘"
}

# ==============================================
# QUẢN LÝ CƠ SỞ DỮ LIỆU
# ==============================================
class CoSoDuLieu:
    @staticmethod
    def tai(filename):
        try:
            with open(f'{filename}.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def luu(data, filename):
        try:
            with open(f'{filename}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Lỗi khi lưu {filename}: {e}")

# Khởi tạo cơ sở dữ liệu
nguoi_dung = CoSoDuLieu.tai('nguoi_dung')
lich_su = CoSoDuLieu.tai('lich_su')
hoat_dong = CoSoDuLieu.tai('hoat_dong')
ma_vip_db = CoSoDuLieu.tai('ma_vip')
moi_ban_db = CoSoDuLieu.tai('moi_ban')
cau_hinh_db = CoSoDuLieu.tai('cau_hinh')
che_do_dao = cau_hinh_db.get('che_do_dao', False)

# ==============================================
# TIỆN ÍCH HỆ THỐNG
# ==============================================
def kiem_tra_thanh_vien_nhom(user_id, nhom_username):
    try:
        # Kiểm tra xem bot có trong nhóm không
        bot_info = bot.get_chat_member(nhom_username, bot.get_me().id)
        if bot_info.status not in ['member', 'administrator', 'creator']:
            print(f"Bot không có trong nhóm {nhom_username}")
            return False
        
        # Kiểm tra trạng thái người dùng
        thanh_vien = bot.get_chat_member(nhom_username, user_id)
        return thanh_vien.status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Lỗi kiểm tra thành viên nhóm {nhom_username}: {e}")
        return False
    except Exception as e:
        print(f"Lỗi không xác định khi kiểm tra nhóm {nhom_username}: {e}")
        return False

def kich_hoat_vip(uid, days=7, mo_rong=False):
    uid = str(uid)
    nguoi_dung[uid] = nguoi_dung.get(uid, {})
    if mo_rong and nguoi_dung[uid].get("vip_het_han"):
        try:
            het_han_hien_tai = datetime.strptime(nguoi_dung[uid]["vip_het_han"], "%Y-%m-%d %H:%M:%S")
            ngay_het_han = (max(datetime.now(), het_han_hien_tai) + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
        except:
            ngay_het_han = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        ngay_het_han = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    
    nguoi_dung[uid]["vip_kich_hoat"] = True
    nguoi_dung[uid]["vip_het_han"] = ngay_het_han
    nguoi_dung[uid]["lan_hoat_dong_cuoi"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    CoSoDuLieu.luu(nguoi_dung, 'nguoi_dung')
    return ngay_het_han

def tao_ma_vip(ma_ten, days, so_lan_su_dung_toi_da=1):
    ma_vip_db[ma_ten] = {
        "days": days,
        "so_lan_su_dung_toi_da": so_lan_su_dung_toi_da,
        "so_lan_su_dung": 0,
        "ngay_tao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nguoi_su_dung": []
    }
    CoSoDuLieu.luu(ma_vip_db, 'ma_vip')
    return ma_vip_db[ma_ten]

def su_dung_ma_vip(ma_ten, user_id):
    if ma_ten not in ma_vip_db:
        return False, f"{BIEU_TUONG['loi']} Mã không hợp lệ!"
    ma = ma_vip_db[ma_ten]
    user_id = str(user_id)
    if user_id in ma["nguoi_su_dung"]:
        return False, f"{BIEU_TUONG['canh_bao']} Bạn đã sử dụng mã này!"
    if ma["so_lan_su_dung"] >= ma["so_lan_su_dung_toi_da"]:
        return False, f"{BIEU_TUONG['dong_ho']} Mã đã hết lượt sử dụng!"
    
    mo_rong = user_id in nguoi_dung and nguoi_dung[user_id].get("vip_kich_hoat")
    ngay_het_han = kich_hoat_vip(user_id, ma["days"], mo_rong)
    ma["so_lan_su_dung"] += 1
    ma["nguoi_su_dung"].append(user_id)
    CoSoDuLieu.luu(ma_vip_db, 'ma_vip')
    return True, f"{BIEU_TUONG['thanh_cong']} Đã kích hoạt VIP {ma['days']} ngày!\n⏳ Hết hạn: {ngay_het_han}"

def theo_doi_hoat_dong(user_id, hanh_dong):
    user_id = str(user_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    hoat_dong[user_id] = hoat_dong.get(user_id, {
        "lan_dau_xem": now,
        "lan_cuoi_xem": now,
        "so_lan_yeu_cau": 0,
        "hanh_dong": []
    })
    hoat_dong[user_id]["lan_cuoi_xem"] = now
    hoat_dong[user_id]["so_lan_yeu_cau"] += 1
    hoat_dong[user_id]["hanh_dong"].append(hanh_dong)
    CoSoDuLieu.luu(hoat_dong, 'hoat_dong')

def tao_ma_moi_ban(user_id):
    ma = f"MOI1NGAY_{user_id}_{int(time.time())}"
    tao_ma_vip(ma, 1, 1)
    return ma

def theo_doi_moi_ban(nguoi_moi_id, nguoi_duoc_moi_id):
    nguoi_moi_id = str(nguoi_moi_id)
    nguoi_duoc_moi_id = str(nguoi_duoc_moi_id)
    
    if nguoi_moi_id not in moi_ban_db:
        moi_ban_db[nguoi_moi_id] = []
    
    if nguoi_duoc_moi_id not in moi_ban_db[nguoi_moi_id]:
        moi_ban_db[nguoi_moi_id].append(nguoi_duoc_moi_id)
        CoSoDuLieu.luu(moi_ban_db, 'moi_ban')
        
        ma_thuong = tao_ma_moi_ban(nguoi_moi_id)
        try:
            bot.send_message(
                nguoi_moi_id,
                f"""
🌟 <b>Mời Bạn Thành Công!</b>
{BIEU_TUONG['thanh_cong']} Bạn đã mời ID {nguoi_duoc_moi_id}!
🔑 Mã thưởng: <code>{ma_thuong}</code>
📋 Dùng: /ma {ma_thuong}
                """,
                parse_mode="HTML"
            )
        except:
            pass

# ==============================================
# ĐỘNG CƠ PHÂN TÍCH MD5
# ==============================================
class PhanTichMD5:
    @staticmethod
    def dong_co_sieu_tri_tue(md5_hash):
        md5_hash = md5_hash.lower().strip()
        if len(md5_hash) != 32 or not re.match(r'^[a-f0-9]{32}$', md5_hash):
            raise ValueError("MD5 không hợp lệ")
        
        hex_bytes = [int(md5_hash[i:i+2], 16) for i in range(0, len(md5_hash), 2)]
        byte_array = np.array(hex_bytes)
        tong = sum(hex_bytes)

        # Thuật toán 1: Siêu Trí Tuệ 7 Động Cơ
        tong_luong_tu = sum(byte_array[i] * math.cos(i * math.pi/16) for i in range(16))
        diem_neural = sum(byte_array[i] * (1.618 ** (i % 5)) for i in range(16))
        chieu_phân_hình = sum(byte_array[i] * (1 + math.sqrt(5)) / 2 for i in range(16))
        diem1 = (tong_luong_tu + diem_neural + chieu_phân_hình) % 20
        ket_qua1 = "TÀI" if diem1 < 10 else "XỈU"
        xac_suat1 = 95 - abs(diem1 - 10) * 4.5 if diem1 < 10 else 50 + (diem1 - 10) * 4.5

        # Thuật toán 2: Kim Cương Trí Tuệ 7
        nums = [int(c, 16) for c in md5_hash]
        trung_binh = sum(nums) / 32
        so_chan = sum(1 for n in nums if n % 2 == 0)
        tren_8 = sum(1 for n in nums if n > 8)
        diem2 = (1 if trung_binh > 7.5 else 0) + (1 if so_chan > 16 else 0) + (1 if tren_8 >= 10 else 0)
        ket_qua2 = "TÀI" if diem2 >= 2 else "XỈU"
        xac_suat2 = 90 if diem2 == 3 else 75 if diem2 == 2 else 60
        xac_suat2 = xac_suat2 if ket_qua2 == "TÀI" else 100 - xac_suat2

        # Thuật toán 3: Công Nghệ Titans
        x = int(md5_hash, 16)
        ket_qua3 = "TÀI" if x % 2 == 0 else "XỈU"
        xac_suat3 = 75.0

        # Kết quả cuối cùng
        trong_so = [0.5, 0.3, 0.2]
        diem_cuoi = (diem1 * trong_so[0] + diem2 * 5 * trong_so[1] + (0 if ket_qua3 == "XỈU" else 10) * trong_so[2])
        ket_qua_cuoi = "TÀI" if diem_cuoi < 10 else "XỈU"
        xac_suat_cuoi = (xac_suat1 * trong_so[0] + xac_suat2 * trong_so[1] + xac_suat3 * trong_so[2])
        
        if che_do_dao:
            ket_qua_cuoi = "XỈU" if ket_qua_cuoi == "TÀI" else "TÀI"
            xac_suat_cuoi = 100 - xac_suat_cuoi

        muc_do_rui_ro = "THẤP" if xac_suat_cuoi > 80 else "TRUNG BÌNH" if xac_suat_cuoi > 60 else "CAO"
        
        return {
            "tong": tong,
            "thuattoan1": {"ket_qua": ket_qua1, "xac_suat": f"{xac_suat1:.1f}%", "diem": diem1},
            "thuattoan2": {"ket_qua": ket_qua2, "xac_suat": f"{xac_suat2:.1f}%", "diem": diem2},
            "thuattoan3": {"ket_qua": ket_qua3, "xac_suat": f"{xac_suat3:.1f}%", "diem": x % 2},
            "cuoi": {"ket_qua": ket_qua_cuoi, "xac_suat": f"{xac_suat_cuoi:.1f}%"},
            "rui_ro": muc_do_rui_ro,
            "thoi_gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "da_dao": che_do_dao
        }

# ==============================================
# GIAO DIỆN NGƯỜI DÙNG (THIẾT KẾ CHỦ ĐỀ VŨ TRỤ)
# ==============================================
class GiaoDienNguoiDung:
    @staticmethod
    def tao_menu_chinh():
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            types.KeyboardButton(f"🌌 Phân Tích MD5"),
            types.KeyboardButton(f"💎 Trạng Thái VIP")
        )
        markup.add(
            types.KeyboardButton(f"📈 Thống Kê"),
            types.KeyboardButton(f"📜 Lịch Sử")
        )
        markup.add(
            types.KeyboardButton(f"📩 Mời Bạn"),
            types.KeyboardButton(f"🆘 Trợ Giúp")
        )
        return markup

    @staticmethod
    def tao_menu_tuong_tac():
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton(f"🆘 Trợ Giúp", callback_data="menu_tro_giup")
        )
        return markup

    @staticmethod
    def tao_thong_bao_ket_qua(md5_input, phan_tich):
        che_do = "ĐẢO" if phan_tich["da_dao"] else "BÌNH THƯỜNG"
        return (
            f"🌌 <b>Hyper-AI Galactic Analysis</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ 🪐 <b>Phiên bản:</b> Siêu Trí Tuệ 7 Pro\n"
            f"│ 🔒 <b>MD5:</b> <code>{md5_input[:8]}...{md5_input[-8:]}</code>\n"
            f"│ 📊 <b>Tổng HEX:</b> <code>{phan_tich['tong']}</code>\n"
            f"│ ⚙️ <b>Chế độ:</b> <code>{che_do}</code>\n"
            f"├━━━━━━━━━━━━━━━━━━━━━━━┤\n"
            f"│ 🌟 <b>Hyper-AI Engine</b>\n"
            f"│ {BIEU_TUONG['tai' if phan_tich['thuattoan1']['ket_qua'] == 'TÀI' else 'xiu']} Dự đoán: <b>{phan_tich['thuattoan1']['ket_qua']}</b>\n"
            f"│ 📈 Xác suất: <code>{phan_tich['thuattoan1']['xac_suat']}</code>\n"
            f"├━━━━━━━━━━━━━━━━━━━━━━━┤\n"
            f"│ 💎 <b>Diamond AI Engine</b>\n"
            f"│ {BIEU_TUONG['tai' if phan_tich['thuattoan2']['ket_qua'] == 'TÀI' else 'xiu']} Dự đoán: <b>{phan_tich['thuattoan2']['ket_qua']}</b>\n"
            f"│ 📈 Xác suất: <code>{phan_tich['thuattoan2']['xac_suat']}</code>\n"
            f"├━━━━━━━━━━━━━━━━━━━━━━━┤\n"
            f"│ 🛸 <b>AI-Tech Titans</b>\n"
            f"│ {BIEU_TUONG['tai' if phan_tich['thuattoan3']['ket_qua'] == 'TÀI' else 'xiu']} Dự đoán: <b>{phan_tich['thuattoan3']['ket_qua']}</b>\n"
            f"│ 📈 Xác suất: <code>{phan_tich['thuattoan3']['xac_suat']}</code>\n"
            f"├━━━━━━━━━━━━━━━━━━━━━━━┤\n"
            f"│ 📊 <b>Thống Kê Thuật Toán</b>\n"
            f"│ 🌟 Hyper-AI Engine: <code>{phan_tich['thuattoan1']['diem']:.2f}</code>\n"
            f"│ 💎 Diamond AI Engine: <code>{phan_tich['thuattoan2']['diem']:.2f}</code>\n"
            f"│ 🛸 CAI-Tech Titans: <code>{phan_tich['thuattoan3']['diem']:.2f}</code>\n"
            f"├━━━━━━━━━━━━━━━━━━━━━━━┤\n"
            f"│ 🎯 <b>Dự Đoán Cuối Cùng</b>\n"
            f"│ {BIEU_TUONG['tai' if phan_tich['cuoi']['ket_qua'] == 'TÀI' else 'xiu']} Kết quả: <b>{phan_tich['cuoi']['ket_qua']}</b>\n"
            f"│ 📈 Độ tin cậy: <code>{phan_tich['cuoi']['xac_suat']}</code>\n"
            f"│ 🚨 Mức rủi ro: <b>{phan_tich['rui_ro']}</b>\n"
            f"│ ⏰ Thời gian: {phan_tich['thoi_gian']}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )

# ==============================================
# QUẢN LÝ DỮ LIỆU
# ==============================================
def luu_du_doan(user_id, md5, phan_tich, la_dung=None):
    user_id = str(user_id)
    lich_su[user_id] = lich_su.get(user_id, [])
    lich_su[user_id].append({
        "md5": md5,
        "du_doan": phan_tich,
        "thoi_gian": phan_tich["thoi_gian"],
        "la_dung": la_dung,
        "cho_phan_hoi": True if la_dung is None else False
    })
    if len(lich_su[user_id]) > 100:
        lich_su[user_id] = lich_su[user_id][-100:]
    CoSoDuLieu.luu(lich_su, 'lich_su')

def kiem_tra_trang_thai_phan_hoi(user_id):
    user_id = str(user_id)
    if user_id in lich_su:
        for muc in lich_su[user_id]:
            if muc.get("cho_phan_hoi", False):
                return True, muc["md5"]
    return False, None

def lay_thong_ke_nguoi_dung(user_id):
    user_id = str(user_id)
    if user_id not in lich_su or not lich_su[user_id]:
        return None
    lich_su_nguoi_dung = lich_su[user_id]
    tong = len(lich_su_nguoi_dung)
    dung = sum(1 for muc in lich_su_nguoi_dung if muc.get("la_dung") is True)
    sai = sum(1 for muc in lich_su_nguoi_dung if muc.get("la_dung") is False)
    do_chinh_xac = dung / tong * 100 if tong > 0 else 0
    return {
        "tong": tong,
        "dung": dung,
        "sai": sai,
        "do_chinh_xac": do_chinh_xac
    }

# ==============================================
# PHẢN HỒI VỚI BIỂU TƯỢNG TỰ ĐỘNG XÓA
# ==============================================
async def gui_phan_hoi_voi_bieu_tuong_va_dang_go(chat_id, tin_nhan, noi_dung_phan_hoi, reply_markup=None):
    tin_nhan_bieu_tuong = bot.send_message(chat_id, random.choice(BIEU_TUONG_PHAN_HOI), reply_to_message_id=tin_nhan.message_id)
    bot.send_chat_action(chat_id, 'typing')
    await asyncio.sleep(random.uniform(0.5, 1.5))
    bieu_tuong_ngau_nhien = random.choice(BIEU_TUONG_TRA_LOI)
    bot.send_message(
        chat_id,
        f"{bieu_tuong_ngau_nhien} {noi_dung_phan_hoi}",
        parse_mode="HTML",
        reply_markup=reply_markup,
        reply_to_message_id=tin_nhan.message_id
    )
    await asyncio.sleep(2)
    try:
        bot.delete_message(chat_id, tin_nhan_bieu_tuong.message_id)
    except:
        pass

# Bao bọc để gọi hàm bất đồng bộ trong ngữ cảnh đồng bộ
def gui_phan_hoi_dong_bo(chat_id, tin_nhan, noi_dung_phan_hoi, reply_markup=None):
    asyncio.run(gui_phan_hoi_voi_bieu_tuong_va_dang_go(chat_id, tin_nhan, noi_dung_phan_hoi, reply_markup))

# ==============================================
# XỬ LÝ LỆNH
# ==============================================
@bot.message_handler(commands=['start'])
def xu_ly_bat_dau(tin_nhan):
    if len(tin_nhan.text.split()) > 1:
        nguoi_moi_id = tin_nhan.text.split()[1]
        if nguoi_moi_id != str(tin_nhan.from_user.id):
            theo_doi_moi_ban(nguoi_moi_id, tin_nhan.from_user.id)
    
    ten = tin_nhan.from_user.first_name or "Nhà Thám Hiểm"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(f"🌌 Xác Minh Nhóm", callback_data="xác_minh_nhóm"))
    noi_dung_phan_hoi = (
        f"🌌 <b>Chào mừng, {ten}, đến với Bot Phân Tích Md5!</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ 🚀 <b>Tham gia các nhóm vũ trụ để nhận VIP MIỄN PHÍ 7 ngày!</b>\n"
        f"│ 👥 https://t.me/+D3RxtnBmm_40MjZl\n"
        f"│ 👥https://t.me/+JdolGoz6KyQ5M2Vl\n"
        f"│ 🪐 Nhấn nút để xác minh và nhận mã!\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, markup)
    theo_doi_hoat_dong(tin_nhan.from_user.id, "bắt_đầu")

@bot.message_handler(commands=['ma'])
def xu_ly_ma(tin_nhan):
    phan = tin_nhan.text.split()
    if len(phan) != 2:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /ma [mã]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    thanh_cong, thong_bao = su_dung_ma_vip(phan[1].upper(), tin_nhan.from_user.id)
    noi_dung_phan_hoi = (
        f"🌌 <b>Kích Hoạt VIP</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ {thong_bao}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"sử_dụng_mã:{phan[1]}")

@bot.message_handler(commands=['quan_tri'])
def xu_ly_quan_tri(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    noi_dung_phan_hoi = (
        f"🌌 <b>Trung Tâm Lệnh Quản Trị</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ 🛡️ /cam [user_id] - Cấm người dùng\n"
        f"│ 🛡️ /bo_cam [user_id] - Bỏ cấm người dùng\n"
        f"│ 🛡️ /thong_tin_nguoi_dung [user_id] - Xem thông tin người dùng\n"
        f"│ 🛡️ /kich_hoat [id] [ngày] - Kích hoạt VIP\n"
        f"│ 🛡️ /huy_kich_hoat [id] - Hủy kích hoạt VIP\n"
        f"│ 🛡️ /tao_ma [mã] [ngày] [lượt] - Tạo mã VIP\n"
        f"│ 🛡️ /danh_sach_ma - Liệt kê tất cả mã VIP\n"
        f"│ 🛡️ /gui [thông_điệp] - Phát tin nhắn\n"
        f"│ 🛡️ /thong_ke - Thống kê hệ thống\n"
        f"│ 🛡️ /dao - Bật/tắt chế độ đảo\n"
        f"│ 🛡️ /danh_sach_nguoi_dung - Liệt kê tất cả người dùng\n"
        f"│ 🛡️ /xoa_lich_su [user_id] - Xóa lịch sử người dùng\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, "lệnh_quản_trị")

@bot.message_handler(commands=['cam'])
def xu_ly_cam(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    phan = tin_nhan.text.split()
    if len(phan) != 2:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /cam [user_id]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    uid = phan[1]
    nguoi_dung[uid] = nguoi_dung.get(uid, {})
    nguoi_dung[uid]["bi_cam"] = True
    CoSoDuLieu.luu(nguoi_dung, 'nguoi_dung')
    try:
        bot.send_message(uid, f"🌌 <b>Bị Cấm!</b> Tài khoản của bạn đã bị cấm!", parse_mode="HTML")
    except:
        pass
    noi_dung_phan_hoi = (
        f"🌌 <b>Quản Lý Người Dùng</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ ✅ Người dùng <code>{uid}</code> đã bị cấm\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"cấm:{uid}")

@bot.message_handler(commands=['bo_cam'])
def xu_ly_bo_cam(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    phan = tin_nhan.text.split()
    if len(phan) != 2:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /bo_cam [user_id]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    uid = phan[1]
    if uid in nguoi_dung:
        nguoi_dung[uid]["bi_cam"] = False
        CoSoDuLieu.luu(nguoi_dung, 'nguoi_dung')
        try:
            bot.send_message(uid, f"🌌 <b>Đã Bỏ Cấm!</b> Tài khoản của bạn đã được bỏ cấm!", parse_mode="HTML")
        except:
            pass
        noi_dung_phan_hoi = (
            f"🌌 <b>Quản Lý Người Dùng</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ✅ Người dùng <code>{uid}</code> đã được bỏ cấm\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    else:
        noi_dung_phan_hoi = (
            f"🌌 <b>Quản Lý Người Dùng</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Người dùng <code>{uid}</code> không tồn tại\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"bỏ_cấm:{uid}")

@bot.message_handler(commands=['thong_tin_nguoi_dung'])
def xu_ly_thong_tin_nguoi_dung(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    phan = tin_nhan.text.split()
    if len(phan) != 2:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /thong_tin_nguoi_dung [user_id]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    uid = phan[1]
    if uid not in nguoi_dung:
        noi_dung_phan_hoi = (
            f"🌌 <b>Thông Tin Người Dùng</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Người dùng <code>{uid}</code> không tồn tại\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    nguoi = nguoi_dung[uid]
    thong_ke = lay_thong_ke_nguoi_dung(uid)
    thong_bao_thong_ke = f"""
│ 📈 Thống Kê:\n
│ {BIEU_TUONG['dung']} Đúng: <code>{thong_ke['dung']}</code>\n
│ {BIEU_TUONG['sai']} Sai: <code>{thong_ke['sai']}</code>\n
│ 📈 Độ chính xác: <code>{thong_ke['do_chinh_xac']:.2f}%</code>
    """ if thong_ke else f"│ ℹ️ Không có thống kê"
    noi_dung_phan_hoi = (
        f"🌌 <b>Thông Tin Người Dùng</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ 👤 ID: <code>{uid}</code>\n"
        f"│ 💎 VIP: <code>{'✅ Kích hoạt' if nguoi.get('vip_kich_hoat') else '❌ Không hoạt động'}</code>\n"
        f"│ ⏳ Hết hạn: <code>{nguoi.get('vip_het_han', 'N/A')}</code>\n"
        f"│ 🚨 Bị cấm: <code>{'✅ Có' if nguoi.get('bi_cam') else '❌ Không'}</code>\n"
        f"{thong_bao_thong_ke}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"thông_tin_nguoi_dung:{uid}")

@bot.message_handler(commands=['danh_sach_nguoi_dung'])
def xu_ly_danh_sach_nguoi_dung(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    if not nguoi_dung:
        noi_dung_phan_hoi = (
            f"🌌 <b>Danh Sách Người Dùng</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ℹ️ Không tìm thấy người dùng!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    danh_sach_nguoi = [f"🌌 <b>Danh Sách Người Dùng</b> 🌌\n╭━━━━━━━━━━━━━━━━━━━━━━━╮"]
    for uid, chi_tiet in nguoi_dung.items():
        trang_thai_vip = "💎 Kích hoạt" if chi_tiet.get("vip_kich_hoat") else "❌ Không hoạt động"
        trang_thai_cam = "🚨 Bị cấm" if chi_tiet.get("bi_cam") else "✅ Hoạt động"
        danh_sach_nguoi.append(
            f"│ 👤 ID: <code>{uid}</code> | {trang_thai_vip} | {trang_thai_cam}"
        )
    danh_sach_nguoi.append(f"╰━━━━━━━━━━━━━━━━━━━━━━━╯")
    noi_dung_phan_hoi = "\n".join(danh_sach_nguoi)
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, "danh_sach_nguoi_dung")

@bot.message_handler(commands=['xoa_lich_su'])
def xu_ly_xoa_lich_su(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    phan = tin_nhan.text.split()
    if len(phan) != 2:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /xoa_lich_su [user_id]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    uid = phan[1]
    if uid in lich_su:
        del lich_su[uid]
        CoSoDuLieu.luu(lich_su, 'lich_su')
        noi_dung_phan_hoi = (
            f"🌌 <b>Quản Lý Người Dùng</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ✅ Đã xóa lịch sử cho người dùng <code>{uid}</code>\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    else:
        noi_dung_phan_hoi = (
            f"🌌 <b>Quản Lý Người Dùng</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Không tìm thấy lịch sử cho người dùng <code>{uid}</code>\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"xóa_lịch_sử:{uid}")

@bot.message_handler(commands=['tro_giup'])
def xu_ly_tro_giup(tin_nhan):
    noi_dung_phan_hoi = (
        f"🌌 <b>Hướng Dẫn Sử Dụng Bot</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ 🌌 /start - Bắt đầu hành trình & nhận VIP\n"
        f"│ 💎 /ma [mã] - Kích hoạt VIP\n"
        f"│ 📈 /thong_ke - Xem thống kê của bạn\n"
        f"│ 📜 /lich_su - Kiểm tra lịch sử dự đoán\n"
        f"│ 📩 /moi - Mời bạn bè\n"
        f"│ 🆘 /tro_giup - Hiển thị hướng dẫn này\n"
        f"│ 👤 /id - Xem thông tin tài khoản\n"
        f"│ 🔍 Gửi mã MD5 32 ký tự để phân tích\n"
        f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
    theo_doi_hoat_dong(tin_nhan.from_user.id, "trợ_giúp")

@bot.message_handler(commands=['id'])
def xu_ly_id(tin_nhan):
    uid = str(tin_nhan.from_user.id)
    ten = tin_nhan.from_user.first_name or "Không Tên"
    trang_thai = "❌ Không hoạt động"
    bieu_tuong_trang_thai = BIEU_TUONG["khoa"]
    het_han_str = "N/A"
    if uid in nguoi_dung and nguoi_dung[uid].get("vip_kich_hoat", False):
        het_han_str = nguoi_dung[uid].get("vip_het_han", "N/A")
        if datetime.now() <= datetime.strptime(het_han_str, "%Y-%m-%d %H:%M:%S"):
            trang_thai = "✅ Kích hoạt"
            bieu_tuong_trang_thai = BIEU_TUONG["vip"]
        else:
            trang_thai = "❌ Hết hạn"
            bieu_tuong_trang_thai = BIEU_TUONG["dong_ho"]
    so_lan_moi = len(moi_ban_db.get(uid, []))
    thong_ke = lay_thong_ke_nguoi_dung(uid)
    thong_bao_thong_ke = f"""
│ 📈 Thống Kê:\n
│ {BIEU_TUONG['dung']} Đúng: <code>{thong_ke['dung']}</code>\n
│ {BIEU_TUONG['sai']} Sai: <code>{thong_ke['sai']}</code>\n
│ 📈 Độ chính xác: <code>{thong_ke['do_chinh_xac']:.2f}%</code>
    """ if thong_ke else f"│ ℹ️ Không có thống kê"
    noi_dung_phan_hoi = (
        f"🌌 <b>Thông Tin Tài Khoản</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ 👤 Tên: <code>{ten}</code>\n"
        f"│ 👤 ID: <code>{uid}</code>\n"
        f"│ {bieu_tuong_trang_thai} Trạng thái VIP: <code>{trang_thai}</code>\n"
        f"│ ⏳ Hết hạn: <code>{het_han_str}</code>\n"
        f"│ 📩 Lượt mời: <code>{so_lan_moi}</code>\n"
        f"{thong_bao_thong_ke}\n"
        f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
    theo_doi_hoat_dong(tin_nhan.from_user.id, "id")

@bot.message_handler(commands=['thong_ke'])
def xu_ly_thong_ke(tin_nhan):
    thong_ke = lay_thong_ke_nguoi_dung(tin_nhan.from_user.id)
    if not thong_ke:
        noi_dung_phan_hoi = (
            f"🌌 <b>Thống Kê Cá Nhân</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ℹ️ Không có thống kê!\n"
            f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        return
    noi_dung_phan_hoi = (
        f"🌌 <b>Thống Kê Cá Nhân</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ {BIEU_TUONG['dung']} Đúng: <code>{thong_ke['dung']}</code>\n"
        f"│ {BIEU_TUONG['sai']} Sai: <code>{thong_ke['sai']}</code>\n"
        f"│ 📈 Tổng: <code>{thong_ke['tong']}</code>\n"
        f"│ 📈 Độ chính xác: <code>{thong_ke['do_chinh_xac']:.2f}%</code>\n"
        f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
    theo_doi_hoat_dong(tin_nhan.from_user.id, "thống_kê")

@bot.message_handler(commands=['lich_su'])
def xu_ly_lich_su(tin_nhan):
    uid = str(tin_nhan.from_user.id)
    if uid not in lich_su or not lich_su[uid]:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lịch Sử Dự Đoán</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ℹ️ Không có lịch sử dự đoán!\n"
            f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        return
    lich_su_nguoi_dung = lich_su[uid][-10:]
    thong_bao_lich_su = [f"🌌 <b>Lịch Sử Dự Đoán (Top 10)</b> 🌌\n╭━━━━━━━━━━━━━━━━━━━━━━━╮"]
    for idx, muc in enumerate(reversed(lich_su_nguoi_dung), 1):
        md5_ngan = f"{muc['md5'][:4]}...{muc['md5'][-4:]}"
        ket_qua = muc.get('du_doan', {}).get('cuoi', {}).get('ket_qua', 'N/A')
        thoi_gian_str = datetime.strptime(muc['thoi_gian'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")
        phan_hoi = BIEU_TUONG['dung'] if muc.get('la_dung') is True else BIEU_TUONG['sai'] if muc.get('la_dung') is False else ""
        thong_bao_lich_su.append(f"│ {idx}. <code>{md5_ngan}</code> → <b>{ket_qua}</b> {phan_hoi} | {thoi_gian_str}")
    thong_bao_lich_su.append(f"╰━━━━━━━━━━━━━━━━━━━━━━━╯")
    noi_dung_phan_hoi = "\n".join(thong_bao_lich_su)
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
    theo_doi_hoat_dong(tin_nhan.from_user.id, "lịch_sử")

@bot.message_handler(commands=['moi'])
def xu_ly_moi(tin_nhan):
    user_id = tin_nhan.from_user.id
    lien_ket_moi = f"https://t.me/{TEN_BOT}?start={user_id}"
    noi_dung_phan_hoi = (
        f"🌌 <b>Mời Bạn Bè</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ 📩 Liên kết mời: <code>{lien_ket_moi}</code>\n"
        f"│ ℹ️ Mời 1 bạn để nhận mã VIP 1 ngày!\n"
        f"│ 📩 Tổng lượt mời: <code>{len(moi_ban_db.get(str(user_id), []))}</code>\n"
        f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
    theo_doi_hoat_dong(tin_nhan.from_user.id, "mời")

@bot.message_handler(commands=['dao'])
def xu_ly_dao(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    global che_do_dao
    che_do_dao = not che_do_dao
    CoSoDuLieu.luu({'che_do_dao': che_do_dao}, 'cau_hinh')
    trang_thai = "BẬT" if che_do_dao else "TẮT"
    noi_dung_phan_hoi = (
        f"🌌 <b>Chế Độ Đảo</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ ✅ Chế độ đảo: <code>{trang_thai}</code>\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"chế_độ_đảo:{trang_thai}")

@bot.message_handler(commands=['tao_ma'])
def xu_ly_tao_ma(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    phan = tin_nhan.text.split()
    if len(phan) != 4:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /tao_ma [mã] [ngày] [lượt]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    ma_ten = phan[1].upper()
    ngay = int(phan[2])
    so_lan_su_dung_toi_da = int(phan[3])
    tao_ma_vip(ma_ten, ngay, so_lan_su_dung_toi_da)
    noi_dung_phan_hoi = (
        f"🌌 <b>Tạo Mã VIP</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ ✅ Đã tạo mã thành công!\n"
        f"│ 💎 Mã: <code>{ma_ten}</code>\n"
        f"│ ⏳ Thời hạn: <code>{ngay} ngày</code>\n"
        f"│ ℹ️ Lượt sử dụng: <code>{so_lan_su_dung_toi_da}</code>\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"tạo_mã:{ma_ten}")

@bot.message_handler(commands=['danh_sach_ma'])
def xu_ly_danh_sach_ma(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    if not ma_vip_db:
        noi_dung_phan_hoi = (
            f"🌌 <b>Danh Sách Mã</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ℹ️ Không có mã nào!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    danh_sach_ma = [f"🌌 <b>Danh Sách Mã</b> 🌌\n╭━━━━━━━━━━━━━━━━━━━━━━━╮"]
    for ma, chi_tiet in ma_vip_db.items():
        danh_sach_ma.append(
            f"""
│ 💎 <b><code>{ma}</code></b>\n
│ ⏳ {chi_tiet['days']} ngày | ℹ️ {chi_tiet['so_lan_su_dung']}/{chi_tiet['so_lan_su_dung_toi_da']}\n
│ ⏰ Tạo: {chi_tiet['ngay_tao']}\n
│ 👤 {len(chi_tiet['nguoi_su_dung'])} người dùng
            """
        )
    danh_sach_ma.append(f"╰━━━━━━━━━━━━━━━━━━━━━━━╯")
    noi_dung_phan_hoi = "\n".join(danh_sach_ma)
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, "danh_sách_mã")

@bot.message_handler(commands=['kich_hoat'])
def xu_ly_kich_hoat(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    phan = tin_nhan.text.split()
    if len(phan) != 3:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /kich_hoat [id] [ngày]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    uid = phan[1]
    ngay = int(phan[2])
    if ngay <= 0:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Số ngày phải lớn hơn 0!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    ngay_het_han = kich_hoat_vip(uid, ngay)
    try:
        bot.send_message(
            uid,
            f"""
🌌 <b>VIP Đã Kích Hoạt</b> 🌌
╭━━━━━━━━━━━━━━━━━━━━━━━╮
│ ✅ VIP của bạn đã được kích hoạt!
│ ⏳ Thời hạn: <code>{ngay} ngày</code>
│ ⏰ Hết hạn: <code>{ngay_het_han}</code>
╰━━━━━━━━━━━━━━━━━━━━━━━╯
            """,
            parse_mode="HTML"
        )
    except:
        pass
    noi_dung_phan_hoi = (
        f"🌌 <b>Kích Hoạt VIP</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ ✅ Đã kích hoạt VIP thành công!\n"
        f"│ 👤 ID: <code>{uid}</code>\n"
        f"│ ⏳ Thời hạn: <code>{ngay} ngày</code>\n"
        f"│ ⏰ Hết hạn: <code>{ngay_het_han}</code>\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"kich_hoat:{uid}")

@bot.message_handler(commands=['huy_kich_hoat'])
def xu_ly_huy_kich_hoat(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    phan = tin_nhan.text.split()
    if len(phan) != 2:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Cú pháp: /huy_kich_hoat [id]\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    uid = phan[1]
    if uid in nguoi_dung:
        nguoi_dung[uid]["vip_kich_hoat"] = False
        nguoi_dung[uid].pop("vip_het_han", None)
        CoSoDuLieu.luu(nguoi_dung, 'nguoi_dung')
        try:
            bot.send_message(
                uid,
                f"""
🌌 <b>VIP Đã Hủy Kích Hoạt</b> 🌌
╭━━━━━━━━━━━━━━━━━━━━━━━╮
│ ❌ VIP của bạn đã bị hủy kích hoạt!
╰━━━━━━━━━━━━━━━━━━━━━━━╯
                """,
                parse_mode="HTML"
            )
        except:
            pass
        noi_dung_phan_hoi = (
            f"🌌 <b>Hủy Kích Hoạt VIP</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ✅ Đã hủy VIP cho ID <code>{uid}</code>\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    else:
        noi_dung_phan_hoi = (
            f"🌌 <b>Hủy Kích Hoạt VIP</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ ID <code>{uid}</code> không tồn tại\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"hủy_kich_hoat:{uid}")

@bot.message_handler(commands=['gui'])
def xu_ly_gui(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    noi_dung = tin_nhan.text[5:].strip()
    if not noi_dung:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lỗi</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Vui lòng nhập thông điệp!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    tong = len(nguoi_dung)
    thanh_cong = 0
    that_bai = 0
    tin_nhan_bieu_tuong = bot.send_message(tin_nhan.chat.id, random.choice(BIEU_TUONG_PHAN_HOI), reply_to_message_id=tin_nhan.message_id)
    bot.send_chat_action(tin_nhan.chat.id, 'typing')
    time.sleep(random.uniform(0.5, 1.5))
    tin_nhan_dang_xu_ly = bot.send_message(
        tin_nhan.chat.id,
        f"""
🌌 <b>Phát Tin</b> 🌌
╭━━━━━━━━━━━━━━━━━━━━━━━╮
│ 📡 Đang gửi đến <code>{tong}</code> người dùng...
╰━━━━━━━━━━━━━━━━━━━━━━━╯
        """,
        parse_mode="HTML"
    )
    for uid in nguoi_dung:
        try:
            bot.send_message(
                uid,
                f"""
🌌 <b>Thông Điệp Hệ Thống</b> 🌌
╭━━━━━━━━━━━━━━━━━━━━━━━╮
│ {noi_dung}
╰━━━━━━━━━━━━━━━━━━━━━━━╯
                """,
                parse_mode="HTML"
            )
            thanh_cong += 1
        except:
            that_bai += 1
        time.sleep(0.1)
    bot.edit_message_text(
        f"""
🌌 <b>Phát Tin</b> 🌌
╭━━━━━━━━━━━━━━━━━━━━━━━╮
│ ✅ Gửi thành công: <code>{thanh_cong}</code>
│ ❌ Thất bại: <code>{that_bai}</code>
│ ℹ️ Tổng người dùng: <code>{tong}</code>
╰━━━━━━━━━━━━━━━━━━━━━━━╯
        """,
        tin_nhan.chat.id,
        tin_nhan_dang_xu_ly.message_id,
        parse_mode="HTML"
    )
    bot.delete_message(tin_nhan.chat.id, tin_nhan_bieu_tuong.message_id)
    theo_doi_hoat_dong(tin_nhan.from_user.id, f"phát_tin:{thanh_cong}/{that_bai}")

@bot.message_handler(commands=['thong_ke'])
def xu_ly_thong_ke_he_thong(tin_nhan):
    if tin_nhan.from_user.id != ADMIN_ID:
        noi_dung_phan_hoi = (
            f"🌌 <b>Truy Cập Bị Từ Chối</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Bạn không có quyền!\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return
    
    # Tính toán thống kê
    tong_nguoi_dung = len(nguoi_dung)
    nguoi_dung_vip = sum(1 for uid in nguoi_dung if nguoi_dung[uid].get("vip_kich_hoat", False))
    nguoi_dung_hoat_dong = sum(1 for uid in hoat_dong if 
                               (datetime.now() - datetime.strptime(hoat_dong[uid]["lan_cuoi_xem"], "%Y-%m-%d %H:%M:%S")).days < 7)
    tong_yeu_cau = sum(int(act.get("so_lan_yeu_cau", 0)) for act in hoat_dong.values())
    tong_du_doan = sum(len(h) for h in lich_su.values())
    du_doan_dung = sum(
        sum(1 for muc in lich_su[uid] if muc.get("la_dung") is True)
        for uid in lich_su
    )
    do_chinh_xac = (du_doan_dung / tong_du_doan * 100) if tong_du_doan > 0 else 0
    tong_moi = sum(len(refs) for refs in moi_ban_db.values())
    
    # Định dạng phản hồi
    noi_dung_phan_hoi = (
        f"🌌 <b>Thống Kê Hệ Thống</b> 🌌\n"
        f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ 👤 Người dùng:\n"
        f"│ ├ Tổng: <code>{tong_nguoi_dung}</code>\n"
        f"│ ├ VIP: <code>{nguoi_dung_vip}</code>\n"
        f"│ ├ Hoạt động (7 ngày): <code>{nguoi_dung_hoat_dong}</code>\n"
        f"│ 📊 Yêu cầu:\n"
        f"│ ├ Tổng: <code>{tong_yeu_cau}</code>\n"
        f"│ ├ Dự đoán: <code>{tong_du_doan}</code>\n"
        f"│ ├ Đúng: <code>{du_doan_dung}</code>\n"
        f"│ ├ Độ chính xác: <code>{do_chinh_xac:.2f}%</code>\n"
        f"│ 📩 Lượt mời: <code>{tong_moi}</code>\n"
        f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
    )
    gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
    theo_doi_hoat_dong(tin_nhan.from_user.id, "thống_kê_hệ_thống")

# ==============================================
# XỬ LÝ NÚT TƯƠNG TÁC
# ==============================================
@bot.callback_query_handler(func=lambda call: True)
def xu_ly_nut_tuong_tac(call):
    user_id = call.from_user.id
    data = call.data
    if data == "xác_minh_nhóm":
        nhom_thieu = kiem_tra_tham_gia_nhom(user_id)
        if not nhom_thieu:
            thanh_cong, thong_bao = su_dung_ma_vip(MA_VIP, user_id)
            noi_dung_phan_hoi = (
                f"🌌 <b>Xác Minh Nhóm</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ {thong_bao}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        else:
            noi_dung_phan_hoi = (
                f"🌌 <b>Xác Minh Nhóm</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ ❌ Vui lòng tham gia các nhóm sau:\n"
                f"│ {''.join(f'👥 {nhom}\n' for nhom in nhom_thieu)}"
                f"│ 🔄 Nhấn lại nút để xác minh\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        bot.edit_message_text(
            noi_dung_phan_hoi,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=GiaoDienNguoiDung.tao_menu_tuong_tac() if not nhom_thieu else call.message.reply_markup
        )
        theo_doi_hoat_dong(user_id, "xác_minh_nhóm")
    elif data.startswith("menu_"):
        menu = data.split("_")[1]
        if menu == "phan_tich":
            noi_dung_phan_hoi = (
                f"🌌 <b>Phân Tích MD5</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ 🔍 Gửi mã MD5 32 ký tự để phân tích\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        elif menu == "vip":
            uid = str(user_id)
            trang_thai = "❌ Không hoạt động"
            het_han_str = "N/A"
            if uid in nguoi_dung and nguoi_dung[uid].get("vip_kich_hoat", False):
                het_han_str = nguoi_dung[uid].get("vip_het_han", "N/A")
                if datetime.now() <= datetime.strptime(het_han_str, "%Y-%m-%d %H:%M:%S"):
                    trang_thai = "✅ Kích hoạt"
                else:
                    trang_thai = "❌ Hết hạn"
            noi_dung_phan_hoi = (
                f"🌌 <b>Trạng Thái VIP</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ 💎 Trạng thái: <code>{trang_thai}</code>\n"
                f"│ ⏳ Hết hạn: <code>{het_han_str}</code>\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        elif menu == "thong_ke":
            thong_ke = lay_thong_ke_nguoi_dung(user_id)
            if not thong_ke:
                noi_dung_phan_hoi = (
                    f"🌌 <b>Thống Kê Cá Nhân</b> 🌌\n"
                    f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                    f"│ ℹ️ Không có thống kê!\n"
                    f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                )
            else:
                noi_dung_phan_hoi = (
                    f"🌌 <b>Thống Kê Cá Nhân</b> 🌌\n"
                    f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                    f"│ {BIEU_TUONG['dung']} Đúng: <code>{thong_ke['dung']}</code>\n"
                    f"│ {BIEU_TUONG['sai']} Sai: <code>{thong_ke['sai']}</code>\n"
                    f"│ 📈 Tổng: <code>{thong_ke['tong']}</code>\n"
                    f"│ 📈 Độ chính xác: <code>{thong_ke['do_chinh_xac']:.2f}%</code>\n"
                    f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                )
        elif menu == "lich_su":
            uid = str(user_id)
            if uid not in lich_su or not lich_su[uid]:
                noi_dung_phan_hoi = (
                    f"🌌 <b>Lịch Sử Dự Đoán</b> 🌌\n"
                    f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                    f"│ ℹ️ Không có lịch sử dự đoán!\n"
                    f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                )
            else:
                lich_su_nguoi_dung = lich_su[uid][-10:]
                thong_bao_lich_su = [f"🌌 <b>Lịch Sử Dự Đoán (Top 10)</b> 🌌\n╭━━━━━━━━━━━━━━━━━━━━━━━╮"]
                for idx, muc in enumerate(reversed(lich_su_nguoi_dung), 1):
                    md5_ngan = f"{muc['md5'][:4]}...{muc['md5'][-4:]}"
                    ket_qua = muc.get('du_doan', {}).get('cuoi', {}).get('ket_qua', 'N/A')
                    thoi_gian_str = datetime.strptime(muc['thoi_gian'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")
                    phan_hoi = BIEU_TUONG['dung'] if muc.get('la_dung') is True else BIEU_TUONG['sai'] if muc.get('la_dung') is False else ""
                    thong_bao_lich_su.append(f"│ {idx}. <code>{md5_ngan}</code> → <b>{ket_qua}</b> {phan_hoi} | {thoi_gian_str}")
                thong_bao_lich_su.append(f"╰━━━━━━━━━━━━━━━━━━━━━━━╯")
                noi_dung_phan_hoi = "\n".join(thong_bao_lich_su)
        elif menu == "moi":
            lien_ket_moi = f"https://t.me/{TEN_BOT}?start={user_id}"
            noi_dung_phan_hoi = (
                f"🌌 <b>Mời Bạn Bè</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ 📩 Liên kết mời: <code>{lien_ket_moi}</code>\n"
                f"│ ℹ️ Mời 1 bạn để nhận mã VIP 1 ngày!\n"
                f"│ 📩 Tổng lượt mời: <code>{len(moi_ban_db.get(str(user_id), []))}</code>\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        elif menu == "tro_giup":
            noi_dung_phan_hoi = (
                f"🌌 <b>Hướng Dẫn Lệnh Vũ Trụ</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ 🌌 /start - Bắt đầu hành trình & nhận VIP\n"
                f"│ 💎 /ma [mã] - Kích hoạt VIP\n"
                f"│ 📈 /thong_ke - Xem thống kê của bạn\n"
                f"│ 📜 /lich_su - Kiểm tra lịch sử dự đoán\n"
                f"│ 📩 /moi - Mời bạn bè\n"
                f"│ 🆘 /tro_giup - Hiển thị hướng dẫn này\n"
                f"│ 👤 /id - Xem thông tin tài khoản\n"
                f"│ 🔍 Gửi mã MD5 32 ký tự để phân tích\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        bot.edit_message_text(
            noi_dung_phan_hoi,
            call.message.chat.id,
            call.message.message_id,
            parse_mode="HTML",
            reply_markup=GiaoDienNguoiDung.tao_menu_tuong_tac()
        )
        theo_doi_hoat_dong(user_id, f"menu:{menu}")

# ==============================================
# XỬ LÝ TIN NHẮN KHÁC
# ==============================================
@bot.message_handler(func=lambda message: True)
def xu_ly_tin_nhan_khac(tin_nhan):
    user_id = str(tin_nhan.from_user.id)
    van_ban = tin_nhan.text.strip().lower()
    
    # Kiểm tra tài khoản bị cấm
    if user_id in nguoi_dung and nguoi_dung[user_id].get("bi_cam", False):
        noi_dung_phan_hoi = (
            f"🌌 <b>Tài Khoản Bị Cấm</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❌ Tài khoản của bạn đã bị cấm!\n"
            f"│ 🆘 Liên hệ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
        return

    # Kiểm tra phản hồi đúng/sai
    cho_phan_hoi, md5_cho = kiem_tra_trang_thai_phan_hoi(user_id)
    if cho_phan_hoi and van_ban in ["đúng", "sai"]:
        la_dung = van_ban == "đúng"
        for muc in lich_su[user_id]:
            if muc["md5"] == md5_cho and muc.get("cho_phan_hoi", False):
                muc["la_dung"] = la_dung
                muc["cho_phan_hoi"] = False
                break
        CoSoDuLieu.luu(lich_su, 'lich_su')
        noi_dung_phan_hoi = (
            f"🌌 <b>Phản Hồi Kết Quả</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ {BIEU_TUONG['thanh_cong']} Đã ghi nhận phản hồi: <b>{van_ban.upper()}</b>\n"
            f"│ 🔍 MD5: <code>{md5_cho[:8]}...{md5_cho[-8:]}</code>\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, f"phản_hồi:{van_ban}:{md5_cho}")
        return

    # Xử lý mã MD5
    if re.match(r'^[a-f0-9]{32}$', van_ban):
        nhom_thieu = kiem_tra_tham_gia_nhom(tin_nhan.from_user.id)
        if nhom_thieu and not kiem_tra_vip_kich_hoat(user_id):
            noi_dung_phan_hoi = (
                f"🌌 <b>Phân Tích MD5</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ ❌ Vui lòng tham gia các nhóm sau:\n"
                f"│ {''.join(f'👥 {nhom}\n' for nhom in nhom_thieu)}"
                f"│ ℹ️ Nhấn /start để xác minh\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
            gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
            theo_doi_hoat_dong(user_id, "phân_tích_md5_thất_bại:chưa_tham_gia_nhóm")
            return
        try:
            phan_tich = PhanTichMD5.dong_co_sieu_tri_tue(van_ban)
            noi_dung_phan_hoi = GiaoDienNguoiDung.tao_thong_bao_ket_qua(van_ban, phan_tich)
            luu_du_doan(user_id, van_ban, phan_tich)
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(f"{BIEU_TUONG['dung']} Đúng", callback_data=f"phan_hoi_dung:{van_ban}"),
                types.InlineKeyboardButton(f"{BIEU_TUONG['sai']} Sai", callback_data=f"phan_hoi_sai:{van_ban}")
            )
            gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, markup)
            theo_doi_hoat_dong(user_id, f"phân_tích_md5:{van_ban}")
        except ValueError as e:
            noi_dung_phan_hoi = (
                f"🌌 <b>Lỗi</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ ❌ {str(e)}\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
            gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi)
            theo_doi_hoat_dong(user_id, f"phân_tích_md5_lỗi:{van_ban}")
        return

    # Xử lý các lệnh văn bản từ menu
    if van_ban == "🌌 phân tích md5":
        noi_dung_phan_hoi = (
            f"🌌 <b>Phân Tích MD5</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ 🔍 Gửi mã MD5 32 ký tự để phân tích\n"
            f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, "phân_tích_md5_menu")
    elif van_ban == "💎 trạng thái vip":
        uid = str(user_id)
        trang_thai = "❌ Không hoạt động"
        het_han_str = "N/A"
        if uid in nguoi_dung and nguoi_dung[uid].get("vip_kich_hoat", False):
            het_han_str = nguoi_dung[uid].get("vip_het_han", "N/A")
            if datetime.now() <= datetime.strptime(het_han_str, "%Y-%m-%d %H:%M:%S"):
                trang_thai = "✅ Kích hoạt"
            else:
                trang_thai = "❌ Hết hạn"
        noi_dung_phan_hoi = (
            f"🌌 <b>Trạng Thái VIP</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ 💎 Trạng thái: <code>{trang_thai}</code>\n"
            f"│ ⏳ Hết hạn: <code>{het_han_str}</code>\n"
            f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, "trạng_thái_vip")
    elif van_ban == "📈 thống kê":
        thong_ke = lay_thong_ke_nguoi_dung(user_id)
        if not thong_ke:
            noi_dung_phan_hoi = (
                f"🌌 <b>Thống Kê Cá Nhân</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ ℹ️ Không có thống kê!\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        else:
            noi_dung_phan_hoi = (
                f"🌌 <b>Thống Kê Cá Nhân</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ {BIEU_TUONG['dung']} Đúng: <code>{thong_ke['dung']}</code>\n"
                f"│ {BIEU_TUONG['sai']} Sai: <code>{thong_ke['sai']}</code>\n"
                f"│ 📈 Tổng: <code>{thong_ke['tong']}</code>\n"
                f"│ 📈 Độ chính xác: <code>{thong_ke['do_chinh_xac']:.2f}%</code>\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, "thống_kê")
    elif van_ban == "📜 lịch sử":
        if user_id not in lich_su or not lich_su[user_id]:
            noi_dung_phan_hoi = (
                f"🌌 <b>Lịch Sử Dự Đoán</b> 🌌\n"
                f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
                f"│ ℹ️ Không có lịch sử dự đoán!\n"
                f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        else:
            lich_su_nguoi_dung = lich_su[user_id][-10:]
            thong_bao_lich_su = [f"🌌 <b>Lịch Sử Dự Đoán (Top 10)</b> 🌌\n╭━━━━━━━━━━━━━━━━━━━━━━━╮"]
            for idx, muc in enumerate(reversed(lich_su_nguoi_dung), 1):
                md5_ngan = f"{muc['md5'][:4]}...{muc['md5'][-4:]}"
                ket_qua = muc.get('du_doan', {}).get('cuoi', {}).get('ket_qua', 'N/A')
                thoi_gian_str = datetime.strptime(muc['thoi_gian'], "%Y-%m-%d %H:%M:%S").strftime("%d/%m %H:%M")
                phan_hoi = BIEU_TUONG['dung'] if muc.get('la_dung') is True else BIEU_TUONG['sai'] if muc.get('la_dung') is False else ""
                thong_bao_lich_su.append(f"│ {idx}. <code>{md5_ngan}</code> → <b>{ket_qua}</b> {phan_hoi} | {thoi_gian_str}")
            thong_bao_lich_su.append(f"╰━━━━━━━━━━━━━━━━━━━━━━━╯")
            noi_dung_phan_hoi = "\n".join(thong_bao_lich_su)
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, "lịch_sử")
    elif van_ban == "📩 mời bạn":
        lien_ket_moi = f"https://t.me/{TEN_BOT}?start={user_id}"
        noi_dung_phan_hoi = (
            f"🌌 <b>Mời Bạn Bè</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ 📩 Liên kết mời: <code>{lien_ket_moi}</code>\n"
            f"│ ℹ️ Mời 1 bạn để nhận mã VIP 1 ngày!\n"
            f"│ 📩 Tổng lượt mời: <code>{len(moi_ban_db.get(str(user_id), []))}</code>\n"
            f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, "mời_bạn")
    elif van_ban == "🆘 trợ giúp":
        noi_dung_phan_hoi = (
            f"🌌 <b>Hướng Dẫn Lệnh Vũ Trụ</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ 🌌 /start - Bắt đầu hành trình & nhận VIP\n"
            f"│ 💎 /ma [mã] - Kích hoạt VIP\n"
            f"│ 📈 /thong_ke - Xem thống kê của bạn\n"
            f"│ 📜 /lich_su - Kiểm tra lịch sử dự đoán\n"
            f"│ 📩 /moi - Mời bạn bè\n"
            f"│ 🆘 /tro_giup - Hiển thị hướng dẫn này\n"
            f"│ 👤 /id - Xem thông tin tài khoản\n"
            f"│ 🔍 Gửi mã MD5 32 ký tự để phân tích\n"
            f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, "trợ_giúp")
    else:
        noi_dung_phan_hoi = (
            f"🌌 <b>Lệnh Không Xác Định</b> 🌌\n"
            f"╭━━━━━━━━━━━━━━━━━━━━━━━╮\n"
            f"│ ❓ Đầu vào không được nhận diện!\n"
            f"│ ℹ️ Dùng /tro_giup để xem danh sách lệnh\n"
            f"│ 🔍 Hoặc gửi mã MD5 32 ký tự\n"
            f"│ 🆘 Hỗ trợ: {LIEN_HE_HO_TRO}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        gui_phan_hoi_dong_bo(tin_nhan.chat.id, tin_nhan, noi_dung_phan_hoi, GiaoDienNguoiDung.tao_menu_tuong_tac())
        theo_doi_hoat_dong(user_id, f"đầu_vào_không_xác_định:{van_ban}")

# ==============================================
# KHỞI TẠO BOT
# ==============================================
def main():
    print("🌌 Trình Phân Tích MD5 Vũ Trụ đã trực tuyến! 🚀")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=5)
    except Exception as e:
        print(f"Lỗi trong quá trình polling: {e}")
        time.sleep(5)
        main()

if __name__ == "__main__":
    main()
