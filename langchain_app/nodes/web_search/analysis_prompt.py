from langchain_app.nodes.web_search.query_prompt import HUMAN_MESSAGE


SYSTEM_MESSAGE = """You are an expert at analyzing educational institutions for M&A purposes.
Given web search results about a target institution, extract relevant information to enhance our understanding
of the institution's current features.

Current Features:
{features}

Web Search Results:
{search_results}

Analyze the search results and enhance the current features with any new, factual information found.
Format your response as a complete, updated feature set that includes both the original information
and any new information from the search results. Maintain the same structure and organization as the
original features.

Only include factual, verifiable information. If information conflicts with the current features,
note both pieces of information and their sources.

Use numbered sources in your report (e.g., [1], [2]) based on information from source documents
        
In the Sources section:
- Include all sources used in your report
- Provide full links to relevant websites or specific document paths
- Separate each source by a newline. Use two spaces at the end of each line to create a newline in Markdown.
- It will look like:

### Sources
[1] Link or Document name
[2] Link or Document name

7. Be sure to combine sources. For example this is not correct:

[3] https://ai.meta.com/blog/meta-llama-3-1/
[4] https://ai.meta.com/blog/meta-llama-3-1/

There should be no redundant sources. It should simply be:

[3] https://ai.meta.com/blog/meta-llama-3-1/

"""

HUMAN_MESSAGE = """Current features:
{features}

Search results:
{search_results}"""