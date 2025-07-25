import os, time, uuid, httpx, logging.handlers
import pymysql as mysql
from datetime import datetime
from dotenv import load_dotenv
from PIL import Image

# Load environment variables from .env file
load_dotenv()

# Configure logging
LOG_FILENAME = f"logs/app-{datetime.now().strftime('%Y%m%d')}.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.handlers.RotatingFileHandler(LOG_FILENAME, maxBytes=10485760, backupCount=5),
                        logging.StreamHandler()
                    ])
log = logging.getLogger(__name__)

# Function definitions
def no_space(s):
    return s.strip().lower().replace(" ", "-")

def generate_image(prompt, name, save_path):
    url = f"{os.getenv('AI_SERVICE_URL')}/prompt/{prompt}-{uuid.uuid4()}?width=500&height=800"

    while True:
        try:
            response = httpx.get(url)
            if response.status_code == 200:
                image_save_name = f"{no_space(name)}.jpg"
                image_save_path = os.path.join(save_path, image_save_name)
                os.makedirs(os.path.dirname(image_save_path), exist_ok=True)

                with open(image_save_path, 'wb') as f:
                    f.write(response.content)

                # Crop watermark/artifacts
                image = Image.open(image_save_path)
                image = image.crop((0, 0, image.width, image.height - 50))
                image.save(image_save_path)

                return image_save_name
            else:
                print(f"Retrying... Status code: {response.status_code}")
        except httpx.HTTPError as e:
            print(f"Request failed: {e}. Retrying...")

        time.sleep(5)  # Avoid rate-limiting

# Main program
if __name__ == '__main__':
    log.info('Ensuring output folder exists')
    save_path = os.getenv('IMAGE_DIR')
    os.makedirs(save_path, exist_ok=True)

    log.info('Connecting to database')
    connection = mysql.connect(host=os.getenv('DB_HOST'), port=int(os.getenv('DB_PORT')),
                               user=os.getenv('DB_USERNAME'),password=os.getenv('DB_PASSWORD'),
                               db=os.getenv('DB_NAME'))

    with connection.cursor() as cursor:
        log.info('Extracting data')
        cursor.execute("""
            SELECT f.film_id, f.title, GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ')
            FROM film f
                JOIN film_actor fa ON f.film_id = fa.film_id
                JOIN actor a ON fa.actor_id = a.actor_id
            GROUP BY f.film_id, f.title
        """)
        films = cursor.fetchall()

        with open('film_poster_data.sql', 'w') as f:
            f.write("USE sakila;\n\n")

            for film in films:
                log.info(f"Generating a poster for {film[0]} : {film[1]}")
                prompt = f"poster for a movie titled {film[1]} with actors: {film[2]}"
                image_path = generate_image(no_space(prompt), f"{film[0]:04} {film[1]}", save_path)
                log.info(f"Generated: {image_path}")

                log.info('Saving the poster to the database')
                query = (f"INSERT INTO film_poster (film_id, poster) VALUES ({film[0]}, '{image_path}')"
                         f" ON DUPLICATE KEY UPDATE poster = VALUES(poster)")
                cursor.execute(query)
                f.write(f"{query};\n")

    log.info('Closing connection')
    connection.commit()
    connection.close()

    log.info("Done!")
