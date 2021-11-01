# moyrascraper

How to run this Scrapy Spider (Requirement: Python Installed)
1. Install virtual environment library
   ```sh
   pip install virtualenv
   ```
2. Create a new virtual environment
   ```sh
   virtualenv myenv
   ```
3. Activate the virtual environment, Mac OS / Linux
   ```sh
   source myenv/bin/activate
   ```
4. Activate the virtual environment Windows
   ```sh
   myenv\Scripts\activate
   ```

5. Copy or Clone this project to your machine
   ```sh
   git clone https://github.com/rural-dev/moyrascraper.git
   ```

6. Install all library in Requirements.txt and Twisted whl.
   ```sh
   pip install -r requirements.txt
   ```
   ```sh
   pip install Twisted-20.3.0-cp38-cp38-win_amd64.whl
   ```

7. There are two spider available `moyra` and `neonail`. You can run the spider using this command and specify output file `scrapy crawl $spidername -o $filename.csv`
   ```sh
   scrapy crawl moyra -o moyra.csv
   ```
   ```sh
   scrapy crawl neonail -o neonail.csv
   ```

