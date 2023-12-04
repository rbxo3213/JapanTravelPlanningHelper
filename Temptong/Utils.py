
class Utils:
    @staticmethod
    def convert_iata_code(iata_code):
        if iata_code in ['HND', 'NRT']:
            return 'TYO'
        if iata_code in ['KIX', 'ITM']:
            return 'OSA'
        return iata_code
    
    @staticmethod
    def convert_price(price):
        conversion_rate = 1350  # Example conversion rate
        return int(float(price) * conversion_rate)

    @staticmethod
    def convert_price_from_jpy_to_krw(price_jpy):
        JPY_TO_KRW_CONVERSION_RATE = 10  # Example rate
        return int(float(price_jpy) * JPY_TO_KRW_CONVERSION_RATE)

    @staticmethod
    def convert_duration(duration):
        try:
            hours = int(duration[2:duration.find('H')])
            minutes = int(duration[duration.find('H')+1:duration.find('M')])
            return f"{hours}h {minutes}m"
        except ValueError:
            return duration

    @staticmethod
    def on_mousewheel(event, canvas):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
