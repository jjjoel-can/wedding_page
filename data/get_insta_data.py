import instaloader

# Initialize Instaloader
L = instaloader.Instaloader()

print(L)

# Define the hashtag to search (e.g., #weddingphotographer)
hashtag = "wedding"

# Load posts for this hashtag
posts = instaloader.Hashtag.from_name(L.context, hashtag).get_posts()

# Loop through posts and extract data
for post in posts:
    print(f"Post URL: https://www.instagram.com/p/{post.shortcode}")
    print(f"Username: {post.owner_username}")
    print(f"Caption: {post.caption}")
    print(f"Likes: {post.likes}")
    print(f"Location: {post.location if post.location else 'No location'}")
    print(f"Date: {post.date}")
    print("-" * 40)
