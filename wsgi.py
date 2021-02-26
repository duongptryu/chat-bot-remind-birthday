from app.main import app, run_bot
import logging
import datetime

if __name__ == "__main__":
    logging.info("start bot " + datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S"))
    run_bot()
    app.run(host='0.0.0.0', port=8080, debug=True)
