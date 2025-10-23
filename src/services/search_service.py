"""
Search service for conversation messages.
"""
from typing import List, Dict, Any, Optional
from services.conversation_manager import ConversationManager


class SearchService:
    """Service for searching through conversation messages."""

    def __init__(self, conversation_manager: ConversationManager) -> None:
        """
        Initialize the search service.

        Args:
            conversation_manager: ConversationManager instance for database access.
        """
        self.conv_manager = conversation_manager

    def search(
        self,
        query: str,
        conversation_id: Optional[int] = None,
        case_sensitive: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search for messages containing the query string.

        Args:
            query: Search query string.
            conversation_id: Optional conversation ID to limit search scope.
            case_sensitive: Whether to perform case-sensitive search.

        Returns:
            List of search results with message and conversation info.
        """
        if not query.strip():
            return []

        # Perform case-insensitive search by default
        # SQLite LIKE is case-insensitive by default
        results = self.conv_manager.search_messages(query, conversation_id)

        # If case-sensitive search is needed, filter results
        if case_sensitive:
            results = [
                r for r in results
                if query in r["content"]
            ]

        return results

    def highlight_matches(self, text: str, query: str, max_context: int = 100) -> str:
        """
        Create a snippet of text with highlighted search matches.

        Args:
            text: Full text content.
            query: Search query to highlight.
            max_context: Maximum characters of context around match.

        Returns:
            Text snippet with match highlighted.
        """
        if not query:
            return text[:max_context * 2] + ("..." if len(text) > max_context * 2 else "")

        # Find first occurrence (case-insensitive)
        lower_text = text.lower()
        lower_query = query.lower()
        pos = lower_text.find(lower_query)

        if pos == -1:
            # No match found, return beginning of text
            return text[:max_context * 2] + ("..." if len(text) > max_context * 2 else "")

        # Calculate snippet boundaries
        start = max(0, pos - max_context)
        end = min(len(text), pos + len(query) + max_context)

        # Extract snippet
        snippet = text[start:end]

        # Add ellipsis if truncated
        if start > 0:
            snippet = "..." + snippet
        if end < len(text):
            snippet = snippet + "..."

        return snippet

    def get_search_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics for search results.

        Args:
            results: List of search results.

        Returns:
            Dictionary with summary statistics.
        """
        if not results:
            return {
                "total_results": 0,
                "conversations_affected": 0,
                "by_role": {},
            }

        # Count by role
        by_role = {}
        for result in results:
            role = result["role"]
            by_role[role] = by_role.get(role, 0) + 1

        # Count unique conversations
        unique_conversations = len(set(r["conversation_id"] for r in results))

        return {
            "total_results": len(results),
            "conversations_affected": unique_conversations,
            "by_role": by_role,
        }
