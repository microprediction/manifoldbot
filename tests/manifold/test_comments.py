"""
Tests for comment functionality in ManifoldBot.
"""

import pytest
from unittest.mock import Mock, patch
from manifoldbot.manifold.comments import Comment, CommentReply, CommentGenerator
from manifoldbot.manifold.writer import ManifoldWriter


class TestComment:
    """Test cases for Comment dataclass."""
    
    def test_comment_creation(self):
        """Test basic comment creation."""
        comment = Comment(
            contractId="market123",
            content="This is a test comment"
        )
        
        assert comment.contractId == "market123"
        assert comment.content == "This is a test comment"
    
    def test_comment_to_dict(self):
        """Test comment serialization."""
        comment = Comment(
            contractId="market123",
            content="Test comment"
        )
        
        result = comment.to_dict()
        
        assert result == {
            'contractId': 'market123',
            'content': 'Test comment'
        }
    
    def test_comment_validation_success(self):
        """Test successful comment validation."""
        comment = Comment(
            contractId="market123",
            content="Valid comment"
        )
        
        # Should not raise any exception
        comment.validate()
    
    def test_comment_validation_empty_contract_id(self):
        """Test comment validation with empty contract ID."""
        comment = Comment(
            contractId="",
            content="Valid content"
        )
        
        with pytest.raises(ValueError, match="Comment must have a contractId"):
            comment.validate()
    
    def test_comment_validation_empty_content(self):
        """Test comment validation with empty content."""
        comment = Comment(
            contractId="market123",
            content=""
        )
        
        with pytest.raises(ValueError, match="Comment content cannot be empty"):
            comment.validate()
    
    def test_comment_validation_too_long(self):
        """Test comment validation with content too long."""
        comment = Comment(
            contractId="market123",
            content="x" * 10001  # Over 10,000 character limit
        )
        
        with pytest.raises(ValueError, match="Comment content too long"):
            comment.validate()


class TestCommentReply:
    """Test cases for CommentReply dataclass."""
    
    def test_reply_creation(self):
        """Test basic reply creation."""
        reply = CommentReply(
            contractId="market123",
            content="This is a reply",
            replyToCommentId="comment456"
        )
        
        assert reply.contractId == "market123"
        assert reply.content == "This is a reply"
        assert reply.replyToCommentId == "comment456"
    
    def test_reply_validation_success(self):
        """Test successful reply validation."""
        reply = CommentReply(
            contractId="market123",
            content="Valid reply",
            replyToCommentId="comment456"
        )
        
        # Should not raise any exception
        reply.validate()
    
    def test_reply_validation_missing_reply_id(self):
        """Test reply validation with missing reply ID."""
        reply = CommentReply(
            contractId="market123",
            content="Valid content",
            replyToCommentId=""
        )
        
        with pytest.raises(ValueError, match="Reply must have a replyToCommentId"):
            reply.validate()


class TestCommentGenerator:
    """Test cases for CommentGenerator class."""
    
    def test_generate_analysis_comment_basic(self):
        """Test basic analysis comment generation."""
        generator = CommentGenerator()
        
        analysis_result = {
            'llm_probability': 0.75,
            'confidence': 0.8,
            'reasoning': 'Strong evidence suggests YES',
            'model_used': 'gpt-4'
        }
        
        comment = generator.generate_analysis_comment(
            market_question="Will it rain tomorrow?",
            current_probability=0.5,
            analysis_result=analysis_result
        )
        
        assert "📊 **Analysis Update**" in comment
        assert "higher than the current market price" in comment
        assert "50.0%" in comment  # Current probability
        assert "75.0%" in comment  # LLM probability
        assert "80.0%" in comment  # Confidence
        assert "Strong evidence suggests YES" in comment
        assert "gpt-4 via ManifoldBot" in comment
    
    def test_generate_analysis_comment_no_reasoning(self):
        """Test analysis comment generation without reasoning."""
        generator = CommentGenerator()
        
        analysis_result = {
            'llm_probability': 0.45,
            'confidence': 0.7,
            'reasoning': 'No reasoning provided',
            'model_used': 'gpt-4'
        }
        
        comment = generator.generate_analysis_comment(
            market_question="Will it rain tomorrow?",
            current_probability=0.5,
            analysis_result=analysis_result,
            include_reasoning=True  # Should still exclude "No reasoning provided"
        )
        
        assert "📊 **Analysis Update**" in comment
        assert "lower than the current market price" in comment
        assert "No reasoning provided" not in comment
    
    def test_generate_trading_comment(self):
        """Test trading comment generation."""
        generator = CommentGenerator()
        
        comment = generator.generate_trading_comment(
            action="BUY",
            market_question="Will it rain tomorrow?",
            current_probability=0.6,
            reasoning="Strong meteorological indicators",
            amount=50
        )
        
        assert "📈 **BUY Signal**" in comment
        assert "Placed buy order for M$50" in comment
        assert "60.0%" in comment
        assert "Strong meteorological indicators" in comment
        assert "ManifoldBot" in comment
    
    def test_generate_custom_comment(self):
        """Test custom comment generation with template."""
        generator = CommentGenerator()
        
        template = "Market: {market_question} | Probability: {current_probability_pct} | Custom: {custom_value}"
        
        comment = generator.generate_custom_comment(
            template=template,
            market_question="Will it rain?",
            current_probability=0.7,
            custom_value="test123"
        )
        
        expected = "Market: Will it rain? | Probability: 70.0% | Custom: test123"
        assert comment == expected


@pytest.fixture
def mock_writer():
    """Create a mock ManifoldWriter for testing."""
    writer = Mock(spec=ManifoldWriter)
    writer.logger = Mock()
    return writer


class TestManifoldWriterComments:
    """Test cases for comment methods in ManifoldWriter."""
    
    @patch('manifoldbot.manifold.writer.ManifoldWriter._make_authenticated_request')
    def test_post_comment(self, mock_request):
        """Test posting a comment."""
        # Setup
        mock_request.return_value = {'id': 'comment123', 'content': 'Test comment'}
        writer = ManifoldWriter(api_key="test_key")
        
        comment = Comment(contractId="market123", content="Test comment")
        
        # Execute
        result = writer.post_comment(comment)
        
        # Verify
        mock_request.assert_called_once_with(
            "POST",
            "/comment",
            json={'contractId': 'market123', 'content': 'Test comment'}
        )
        assert result['id'] == 'comment123'
    
    @patch('manifoldbot.manifold.writer.ManifoldWriter._make_authenticated_request')
    def test_post_simple_comment(self, mock_request):
        """Test posting a simple comment using convenience method."""
        # Setup
        mock_request.return_value = {'id': 'comment456'}
        writer = ManifoldWriter(api_key="test_key")
        
        # Execute
        result = writer.post_simple_comment("market123", "Simple test comment")
        
        # Verify
        mock_request.assert_called_once_with(
            "POST",
            "/comment",
            json={'contractId': 'market123', 'content': 'Simple test comment'}
        )
        assert result['id'] == 'comment456'
    
    @patch('manifoldbot.manifold.writer.ManifoldWriter._make_authenticated_request')
    def test_post_analysis_comment(self, mock_request):
        """Test posting an analysis comment."""
        # Setup
        mock_request.return_value = {'id': 'analysis_comment'}
        writer = ManifoldWriter(api_key="test_key")
        
        # Execute
        result = writer.post_analysis_comment(
            market_id="market123",
            probability_estimate=0.75,
            reasoning="Strong evidence",
            confidence=0.8
        )
        
        # Verify
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        assert call_args[0][0] == "POST"
        assert call_args[0][1] == "/comment"
        
        comment_content = call_args[1]['json']['content']
        assert "75.0% probability" in comment_content
        assert "80.0%" in comment_content  # Confidence
        assert "Strong evidence" in comment_content
        assert "ManifoldBot" in comment_content
    
    @patch('manifoldbot.manifold.writer.ManifoldWriter._make_authenticated_request')
    def test_get_market_comments(self, mock_request):
        """Test retrieving market comments."""
        # Setup
        mock_comments = [
            {'id': 'comment1', 'content': 'First comment'},
            {'id': 'comment2', 'content': 'Second comment'}
        ]
        mock_request.return_value = mock_comments
        writer = ManifoldWriter(api_key="test_key")
        
        # Execute
        result = writer.get_market_comments("market123", limit=10)
        
        # Verify
        mock_request.assert_called_once_with(
            "GET",
            "/comments",
            params={'limit': 10, 'contractId': 'market123'}
        )
        assert len(result) == 2
        assert result[0]['id'] == 'comment1'
    
    @patch('manifoldbot.manifold.writer.ManifoldWriter._make_authenticated_request')
    def test_edit_comment(self, mock_request):
        """Test editing a comment."""
        # Setup
        mock_request.return_value = {'id': 'comment123', 'content': 'Updated content'}
        writer = ManifoldWriter(api_key="test_key")
        
        # Execute
        result = writer.edit_comment("comment123", "Updated content")
        
        # Verify
        mock_request.assert_called_once_with(
            "POST",
            "/comment/comment123/edit",
            json={'content': 'Updated content'}
        )
        assert result['content'] == 'Updated content'
    
    def test_edit_comment_empty_content(self):
        """Test editing comment with empty content raises error."""
        writer = ManifoldWriter(api_key="test_key")
        
        with pytest.raises(ValueError, match="Comment content cannot be empty"):
            writer.edit_comment("comment123", "")
    
    @patch('manifoldbot.manifold.writer.ManifoldWriter._make_authenticated_request')
    def test_delete_comment(self, mock_request):
        """Test deleting a comment."""
        # Setup
        mock_request.return_value = {'success': True}
        writer = ManifoldWriter(api_key="test_key")
        
        # Execute
        result = writer.delete_comment("comment123")
        
        # Verify
        mock_request.assert_called_once_with(
            "POST",
            "/comment/comment123/delete"
        )
        assert result['success'] is True
    
    @patch('manifoldbot.manifold.writer.ManifoldWriter._make_authenticated_request')
    def test_like_comment(self, mock_request):
        """Test liking a comment."""
        # Setup
        mock_request.return_value = {'liked': True}
        writer = ManifoldWriter(api_key="test_key")
        
        # Execute
        result = writer.like_comment("comment123")
        
        # Verify
        mock_request.assert_called_once_with(
            "POST",
            "/comment/comment123/like"
        )
        assert result['liked'] is True