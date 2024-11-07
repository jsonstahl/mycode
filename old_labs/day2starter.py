import requests

def main():
    # Get user input for band and song (with defaults)
    band = input("Enter the band name (default: 'Beatles'): ") or "Beatles"
    song = input("Enter the song title (default: 'Let it Be'): ") or "Let it Be"

    # Construct the URL
    url = f"https://api.lyrics.ovh/v1/{band}/{song}".replace(" ", "%20")
    print(url)

    # Send GET request
    response = requests.get(url)
    if response.status_code == 200:
        print(response.json())

if __name__ == "__main__":
    main()
