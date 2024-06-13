import qrcode
import base64
from io import BytesIO

def generate_pix_code(merchant_name, city, transaction_amount, pix_key):
    payload_format_indicator = "00"
    point_of_initiation_method = "01"  # Set this to "12" if the QR code is reusable
    merchant_account_information = "26"
    merchant_account_information_gui = "0014br.gov.bcb.pix"
    merchant_account_information_key = f"01{len(pix_key):02d}{pix_key}"
    merchant_account_information_category_code = "52040000"
    merchant_account_information_country_code = "5802BR"
    merchant_account_information_merchant_name = f"59{len(merchant_name):02d}{merchant_name}"
    merchant_account_information_merchant_city = f"60{len(city):02d}{city}"
    transaction_currency = "5303986"
    transaction_amount_formatted = f"54{len(f'{transaction_amount:.2f}'):02d}{transaction_amount:.2f}"
    additional_data_field_template = "62"
    additional_data_field_template_reference_label = "05"+"20"+"mpqrinter8010936787463042CF0"

    crc16 = "6304"  # This needs to be calculated

    payload = (
        f"{payload_format_indicator}01{point_of_initiation_method}"
        f"{merchant_account_information}{merchant_account_information_gui}{merchant_account_information_key}"
        f"{merchant_account_information_category_code}{transaction_currency}{transaction_amount_formatted}"
        f"{merchant_account_information_country_code}{merchant_account_information_merchant_name}"
        f"{merchant_account_information_merchant_city}{additional_data_field_template}"
        f"{additional_data_field_template_reference_label}{crc16}"
    )

    # Calculate the CRC16 checksum
    crc = crc16_ccitt(payload)
    payload += crc

    return payload

def crc16_ccitt(payload):
    crc = 0xFFFF
    polynom = 0x1021

    for byte in payload.encode():
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ polynom
            else:
                crc <<= 1
            crc &= 0xFFFF  # Trim to 16 bits
    return f"{crc:04X}"

def generate_qr_code(pix_code):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(pix_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    base64_qr = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return base64_qr

# Exemplo de uso
merchant_name = "PEDRO PERES"
city = "Sorocaba"
transaction_amount = 100.00
pix_key = "7f07e6ec-2076-44e4-bfa6-07c1281ea920"

pix_code = generate_pix_code(merchant_name, city, transaction_amount, pix_key)
base64_qr = generate_qr_code(pix_code)

print({
    "clipboard": pix_code,
    "id": 80109367874,
    "qrcode": f"data:image/jpeg;base64,{base64_qr}"
})
