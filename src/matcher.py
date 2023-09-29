from clustering.clustering import get_clusters
from searchers.bm25_searcher.bm25_search import BM25Searcher

from shared.models import LinkingMethod


class Matcher:
    def __init__(self, texts, embeddings, dates):
        self.embeddings = embeddings
        self.texts = texts
        self.dates = dates

    def get_stories(self, method, **args):
        if method == LinkingMethod.DBSCAN:
            stories_nums = get_clusters(self.embeddings, **args)
        elif method == LinkingMethod.BM25:
            searcher = BM25Searcher(self.texts, self.embeddings)
            stories_nums = []
            noise_cluster = []
            for i in range(len(self.texts)):
                top, noise = searcher.search_in_deep(text_num=i, **args)
                if top and not (noise):
                    stories_nums.append(top)
                else:
                    noise_cluster.extend(top)
            stories_nums.append(noise_cluster)
        else:
            raise AttributeError(f"Unexpected linking method {method}")

        stories = []
        for i in range(len(stories_nums)):
            story_date = [self.dates[i] for i in stories_nums[i]]
            stories_nums[i] = [
                x for _, x in sorted(zip(story_date, stories_nums[i]))
            ]
            story = []
            for num in stories_nums[i]:
                story.append(self.texts[num])
            stories.append(story)
        return stories, stories_nums
