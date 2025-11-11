# recommender.py

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------
# 1) Sample data creation
# ---------------------------
def create_sample_data():
    # Items (movies/books/products) with textual info (title + genres + tags)
    items = [
        (1, "The Space Odyssey", "sci-fi space future adventure"),
        (2, "Love in Paris", "romance drama europe love"),
        (3, "Python for Data", "education programming python data science"),
        (4, "Galaxy Wars", "sci-fi action space war"),
        (5, "The Chef's Table", "cooking food documentary"),
        (6, "Romantic Getaway", "romance travel drama"),
        (7, "Deep Learning", "education ai deep-learning neural-networks"),
        (8, "Action Heroes", "action adventure thriller"),
        (9, "Space Cooking", "sci-fi cooking comedy"),
        (10,"Data Stories", "education data visualization stories"),
    ]
    items_df = pd.DataFrame(items, columns=["item_id","title","description"])

    # Ratings (user_id, item_id, rating)
    # Create some synthetic users with tastes
    ratings = [
        (101, 1, 5), (101, 4, 4), (101, 9, 4),    # sci-fi lover
        (102, 2, 5), (102, 6, 4),                 # romance lover
        (103, 3, 5), (103, 7, 4), (103, 10,4),    # data/education lover
        (104, 8, 5), (104, 4, 3),                 # action fan
        (105, 5, 5), (105, 9, 3),                 # cooking / documentary
        (106, 1, 4), (106, 3, 3), (106, 7, 5),    # mixed: sci-fi + data
    ]
    ratings_df = pd.DataFrame(ratings, columns=["user_id","item_id","rating"])

    return items_df, ratings_df

# ---------------------------
# 2) Content-based recommender
# ---------------------------
class ContentBasedRecommender:
    def __init__(self):
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.item_matrix = None
        self.items_df = None

    def fit(self, items_df):
        """
        items_df must have columns: item_id, title, description (text)
        """
        self.items_df = items_df.copy().reset_index(drop=True)
        # Combine title + description
        corpus = (self.items_df["title"] + " " + self.items_df["description"]).values
        self.item_matrix = self.tfidf.fit_transform(corpus)
        print("[ContentBased] Fit complete — items:", len(self.items_df))

    def recommend_for_item(self, item_id, top_n=5):
        # find item index
        idx = self.items_df.index[self.items_df["item_id"] == item_id].tolist()
        if not idx:
            return []
        idx = idx[0]
        sims = cosine_similarity(self.item_matrix[idx], self.item_matrix).flatten()
        # exclude itself
        sims[idx] = -1
        top_idx = sims.argsort()[::-1][:top_n]
        return self.items_df.iloc[top_idx][["item_id","title"]].to_dict(orient="records")

    def recommend_for_user_profile(self, liked_item_ids, top_n=5):
        """
        liked_item_ids: list of item_ids that user likes -> build profile by averaging TF-IDF vectors
        """
        indices = [self.items_df.index[self.items_df["item_id"] == iid].tolist() for iid in liked_item_ids]
        indices = [i[0] for i in indices if i]
        if not indices:
            return []
        profile = self.item_matrix[indices].mean(axis=0)
        sims = cosine_similarity(profile, self.item_matrix).flatten()
        # remove already liked
        for i in indices:
            sims[i] = -1
        top_idx = sims.argsort()[::-1][:top_n]
        return self.items_df.iloc[top_idx][["item_id","title"]].to_dict(orient="records")

# ---------------------------
# 3) Collaborative (user-based) recommender
# ---------------------------
class UserBasedCollaborative:
    def __init__(self):
        self.user_item_matrix = None
        self.users = None
        self.items = None
        self.user_sim = None

    def fit(self, ratings_df):
        """
        ratings_df: columns user_id, item_id, rating
        Builds user-item rating matrix (users x items), fills missing with 0 (or mean-centered later).
        """
        pivot = ratings_df.pivot_table(index="user_id", columns="item_id", values="rating")
        # Fill NaN with 0 (could also use mean-imputation)
        self.user_item_matrix = pivot.fillna(0)
        self.users = self.user_item_matrix.index.tolist()
        self.items = self.user_item_matrix.columns.tolist()
        # compute user-user cosine similarity
        self.user_sim = cosine_similarity(self.user_item_matrix)
        print("[Collaborative] Fit complete — users:", len(self.users), "items:", len(self.items))

    def recommend(self, user_id, top_n=5):
        if user_id not in self.users:
            return []
        uid_index = self.users.index(user_id)
        sim_scores = self.user_sim[uid_index]
        # Weighted sum of other users' ratings
        # compute predicted scores for all items: sim . ratings / sum(sim)
        # but exclude target user's own ratings
        ratings_matrix = self.user_item_matrix.values
        sim_weights = sim_scores.reshape(1, -1)  # (1, num_users)
        # weighted sum: sim_weights.dot(ratings_matrix) -> (1, num_items)
        numerator = sim_weights.dot(ratings_matrix)
        denom = np.abs(sim_weights).sum()
        # avoid divide by zero
        if denom == 0:
            preds = numerator.flatten()
        else:
            preds = (numerator / denom).flatten()
        # mask already-rated items by this user
        user_ratings = ratings_matrix[uid_index]
        preds[user_ratings > 0] = -np.inf
        # get top indices
        top_k_idx = np.argsort(preds)[::-1][:top_n]
        recommended_items = [self.items[i] for i in top_k_idx if preds[i] != -np.inf]
        # return as list of dicts
        return [{"item_id": iid, "pred_score": float(preds[self.items.index(iid)])} for iid in recommended_items]

# ---------------------------
# 4) Demo / Putting it together
# ---------------------------
def demo():
    items_df, ratings_df = create_sample_data()
    print("\n=== Items ===")
    print(items_df[['item_id','title']])

    print("\n=== Ratings sample ===")
    print(ratings_df.head())

    # Content-based
    cb = ContentBasedRecommender()
    cb.fit(items_df)

    # Example: recommend similar to item_id=1
    print("\n[CB] Similar to item 1 (The Space Odyssey):")
    print(cb.recommend_for_item(1, top_n=4))

    # Build a user profile from liked items (e.g., user likes sci-fi: items 1 and 4)
    user_profile_likes = [1,4]
    print("\n[CB] Recommend for user profile (likes items 1 & 4):")
    print(cb.recommend_for_user_profile(user_profile_likes, top_n=5))

    # Collaborative
    collab = UserBasedCollaborative()
    collab.fit(ratings_df)

    # Recommend for user 101 (sci-fi lover)
    print("\n[Collab] Recommendations for user 101:")
    print(collab.recommend(101, top_n=5))

    # Recommend for a new user not in matrix (cold-start) -> fallback to content-based
    new_user_likes = [3,7]  # e.g., likes data books
    print("\n[Hybrid idea] New user (not in ratings) fallback to CB using liked items [3,7]:")
    print(cb.recommend_for_user_profile(new_user_likes, top_n=5))

if __name__ == "__main__":
    demo()