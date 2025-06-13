"""Streamlit dashboard for Google Business Analytics."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import asyncio
import sys
import os
import time
import random
from typing import Dict, List, Any, Tuple, Optional


# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# DEBUG: Print Azure OpenAI environment variables at startup
logger.info(f"[DEBUG] ENV AZURE_OPENAI_ENDPOINT: {os.getenv('AZURE_OPENAI_ENDPOINT')}")
logger.info(f"[DEBUG] ENV AZURE_OPENAI_API_KEY present: {'YES' if os.getenv('AZURE_OPENAI_API_KEY') and len(os.getenv('AZURE_OPENAI_API_KEY')) > 10 else 'NO'}")
logger.info(f"[DEBUG] ENV AZURE_OPENAI_DEPLOYMENT_NAME: {os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')}")

# Add project root to path to ensure imports work
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    # Import Azure OpenAI service
    from google_business_analytics.shared.azure_openai_service import AzureOpenAIService
except ImportError:
    # Fallback to direct import
    sys.path.append(str(project_root / "src"))
    from google_business_analytics.shared.azure_openai_service import AzureOpenAIService

# Set page config
st.set_page_config(
    page_title="Williams Sonoma Store Analytics Dashboard",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://modelcontextprotocol.io',
        'Report a bug': 'https://github.com/modelcontextprotocol/create-python-server/issues',
        'About': 'Williams Sonoma Store Analytics Dashboard powered by MCP Protocol'
    }
)

# Custom CSS for enhanced styling with improved colors and readability
st.markdown("""
<style>    /* Dark theme main containers */
    .main > div {
        padding: 2rem 3rem 3rem 3rem;
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        min-height: 100vh;
        color: #e2e8f0;
    }
      /* Global text color overrides for dark theme */
    .stMarkdown, .stMarkdown p, .stMarkdown div, .stText {
        color: #e2e8f0 !important;
    }
    
    /* Additional dark theme overrides */
    .stSelectbox label, .stTextInput label, .stTextArea label {
        color: #e2e8f0 !important;
    }
    
    /* Streamlit metric styling for dark theme */
    [data-testid="metric-container"] {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="metric-container"] > div {
        color: #e2e8f0 !important;
    }
    
    /* FAQ section dark theme */
    .faq-category-title {
        color: #94a3b8 !important;
    }
    
    .faq-item {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
    }
    
    .faq-question {
        color: #e2e8f0 !important;
    }
    
    .faq-answer {
        background: #374151;
        color: #d1d5db !important;
    }
      /* Dark theme headers */
    h1, h2, h3 {
        color: #f1f5f9;
        margin-top: 1.5rem !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    h1 {
        font-size: 2.5rem !important;
        color: #60a5fa;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem !important;
    }
    h2 {
        font-size: 1.8rem !important;
        color: #cbd5e1;
        border-bottom: 2px solid #64748b;
        padding-bottom: 0.3rem;
        margin-bottom: 1rem !important;
    }
    h3 {
        font-size: 1.4rem !important;
        margin-bottom: 0.8rem !important;
        color: #94a3b8;
    }
    h4, h5 {
        margin-top: 1rem !important;
        color: #94a3b8;
    }    /* Dark theme card styling */
    .card-container {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3), 0 5px 15px rgba(0, 0, 0, 0.2);
        padding: 2.5rem;
        margin-bottom: 2rem;
        border: 1px solid #475569;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        color: #e2e8f0;
    }
    .card-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4), 0 10px 25px rgba(0, 0, 0, 0.3);
        border-color: #64748b;
        background: linear-gradient(145deg, #334155 0%, #475569 100%);
    }    .card-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
        opacity: 0.8;
    }    /* Dark theme metric containers */
    .metric-container {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        padding: 2rem;
        border-radius: 18px;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 0 4px 15px rgba(0, 0, 0, 0.2);
        border: 2px solid #475569;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        backdrop-filter: blur(10px);
        color: #e2e8f0;
    }
    .metric-container:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 8px 25px rgba(0, 0, 0, 0.3);
        border-color: #64748b;
        background: linear-gradient(145deg, #334155 0%, #475569 100%);
    }
    .metric-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
        border-radius: 18px 18px 0 0;
        opacity: 0.9;
    }    /* Dark theme alert styling */
    .alert-high {
        background: linear-gradient(135deg, #451a03 0%, #7c2d12 50%, #991b1b 100%);
        border-left: 8px solid #ef4444;
        padding: 2rem;
        margin: 1.5rem 0;
        border-radius: 0 15px 15px 0;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3), 0 3px 10px rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        font-weight: 600;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .alert-high:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 35px rgba(239, 68, 68, 0.4), 0 5px 15px rgba(239, 68, 68, 0.3);
    }
    .alert-medium {
        background: linear-gradient(135deg, #451a03 0%, #92400e 50%, #a16207 100%);
        border-left: 8px solid #f59e0b;
        padding: 2rem;
        margin: 1.5rem 0;
        border-radius: 0 15px 15px 0;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3), 0 3px 10px rgba(245, 158, 11, 0.2);
        color: #fde047;
        font-weight: 600;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .alert-medium:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 35px rgba(245, 158, 11, 0.4), 0 5px 15px rgba(245, 158, 11, 0.3);
    }
    .alert-low {
        background: linear-gradient(135deg, #052e16 0%, #14532d 50%, #166534 100%);
        border-left: 8px solid #22c55e;
        padding: 2rem;
        margin: 1.5rem 0;
        border-radius: 0 15px 15px 0;
        box-shadow: 0 8px 25px rgba(34, 197, 94, 0.3), 0 3px 10px rgba(34, 197, 94, 0.2);
        color: #86efac;
        font-weight: 600;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .alert-low:hover {
        transform: translateX(5px);
        box-shadow: 0 12px 35px rgba(34, 197, 94, 0.4), 0 5px 15px rgba(34, 197, 94, 0.3);
    }/* Enhanced badge styling with improved gradients and contrast */
    .badge {
        display: inline-block;
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-size: 0.85rem;
        font-weight: 700;
        margin-right: 0.8rem;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1), 0 2px 8px rgba(0,0,0,0.05);
        transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 2px solid transparent;
        backdrop-filter: blur(10px);
    }
    .badge:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15), 0 4px 15px rgba(0,0,0,0.1);
    }
    .badge-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%);
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .badge-success:hover {
        border-color: #10b981;
        box-shadow: 0 8px 25px rgba(16, 185, 129, 0.3), 0 4px 15px rgba(16, 185, 129, 0.2);
    }
    .badge-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 50%, #b45309 100%);
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .badge-warning:hover {
        border-color: #f59e0b;
        box-shadow: 0 8px 25px rgba(245, 158, 11, 0.3), 0 4px 15px rgba(245, 158, 11, 0.2);
    }
    .badge-danger {
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 50%, #b91c1c 100%);
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .badge-danger:hover {
        border-color: #ef4444;
        box-shadow: 0 8px 25px rgba(239, 68, 68, 0.3), 0 4px 15px rgba(239, 68, 68, 0.2);
    }
    .badge-info {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 50%, #1d4ed8 100%);
        color: white;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .badge-info:hover {
        border-color: #3b82f6;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.3), 0 4px 15px rgba(59, 130, 246, 0.2);
    }
    
    /* Dashboard sections */
    .section-title {
        display: flex;
        align-items: center;
        margin-bottom: 1rem;
    }
    .section-title-line {
        flex-grow: 1;
        height: 1px;
        background-color: #E5E7EB;
        margin-left: 1rem;
    }    /* Dark theme sidebar */
    .css-1aumxhk, .css-ocqkz7 {
        background: linear-gradient(180deg, #1e293b 0%, #334155 50%, #475569 100%) !important;
        color: #e2e8f0 !important;
        box-shadow: 2px 0 15px rgba(0, 0, 0, 0.3) !important;
        border-right: 1px solid #475569 !important;
    }
    .css-629wbf, .css-u8hs99 {
        background: linear-gradient(180deg, #1e293b 0%, #334155 50%, #475569 100%) !important;
        color: #e2e8f0 !important;
        box-shadow: 2px 0 15px rgba(0, 0, 0, 0.3) !important;
        border-right: 1px solid #475569 !important;
    }
      /* Enhanced server status indicators with better animations */
    .status-indicator {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 15px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
        border: 2px solid rgba(255,255,255,0.3);
    }
    @keyframes pulse {
        0% { 
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
        70% { 
            box-shadow: 0 0 0 15px rgba(34, 197, 94, 0);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
            transform: scale(1);
        }
    }
    .status-online {
        background: radial-gradient(circle, #10b981 0%, #059669 50%, #047857 100%);
        border-color: rgba(16, 185, 129, 0.5);
    }
    .status-warning {
        background: radial-gradient(circle, #f59e0b 0%, #d97706 50%, #b45309 100%);
        animation: pulse-warning 2s infinite;
        border-color: rgba(245, 158, 11, 0.5);
    }
    @keyframes pulse-warning {
        0% { 
            box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7);
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
        70% { 
            box-shadow: 0 0 0 15px rgba(245, 158, 11, 0);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(245, 158, 11, 0);
            transform: scale(1);
        }
    }
    .status-offline {
        background: radial-gradient(circle, #ef4444 0%, #dc2626 50%, #b91c1c 100%);
        animation: pulse-danger 2s infinite;
        border-color: rgba(239, 68, 68, 0.5);
    }
    @keyframes pulse-danger {
        0% { 
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
            transform: scale(1);
        }
        50% {
            transform: scale(1.1);
        }
        70% { 
            box-shadow: 0 0 0 15px rgba(239, 68, 68, 0);
        }
        100% { 
            box-shadow: 0 0 0 0 rgba(239, 68, 68, 0);
            transform: scale(1);
        }
    }    /* Dark theme AI section */
    .ai-section {
        background: linear-gradient(135deg, #0c4a6e 0%, #075985 50%, #0369a1 100%);
        border-radius: 20px;
        padding: 2.5rem;
        border: 3px solid rgba(59, 130, 246, 0.3);
        margin: 2rem 0;
        box-shadow: 0 15px 40px rgba(59, 130, 246, 0.2), 0 5px 20px rgba(59, 130, 246, 0.1);
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        color: #e0f2fe;
    }
    .ai-section:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 50px rgba(59, 130, 246, 0.25), 0 8px 25px rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.5);
    }
    .ai-section::before {
        content: "🤖";
        position: absolute;
        top: 1.5rem;
        right: 1.5rem;
        font-size: 2.5rem;
        opacity: 0.8;
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));
    }
    .ai-section h3 {
        color: #bae6fd;
        margin-top: 0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        font-weight: 600;
    }
      /* Dark theme strength and weakness items */
    .strength-item {
        padding: 1rem;
        background: linear-gradient(135deg, #052e16 0%, #14532d 100%);
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border-left: 4px solid #22c55e;
        box-shadow: 0 3px 10px rgba(34, 197, 94, 0.3);
        transition: transform 0.2s ease;
        color: #86efac;
    }
    .strength-item:hover {
        transform: translateX(5px);
    }
    .weakness-item {
        padding: 1rem;
        background: linear-gradient(135deg, #451a03 0%, #7c2d12 100%);
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border-left: 4px solid #ef4444;
        box-shadow: 0 3px 10px rgba(239, 68, 68, 0.3);
        transition: transform 0.2s ease;
        color: #fca5a5;
    }
    .weakness-item:hover {
        transform: translateX(5px);
    }/* Dark theme Q&A section */
    .qa-container {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border-radius: 20px;
        padding: 2.5rem;
        margin: 2rem 0;
        border: 3px solid rgba(100, 116, 139, 0.3);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.3), 0 5px 20px rgba(0, 0, 0, 0.2);
        position: relative;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        color: #e2e8f0;
    }
    .qa-container:hover {
        transform: translateY(-3px);
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), 0 8px 25px rgba(0, 0, 0, 0.3);
        border-color: rgba(100, 116, 139, 0.5);
    }
    .qa-container::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6 0%, #6366f1 50%, #8b5cf6 100%);
        border-radius: 20px 20px 0 0;
        opacity: 0.9;
    }
    .qa-answer {
        background: linear-gradient(135deg, #374151 0%, #4b5563 50%, #6b7280 100%);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 1.5rem;
        border-left: 6px solid #60a5fa;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2), 0 3px 10px rgba(59, 130, 246, 0.1);
        color: #f1f5f9;
        line-height: 1.7;
        font-weight: 500;
        backdrop-filter: blur(5px);
    }
    
    /* FAQ section */
    .faq-category {
        margin-bottom: 2rem;
    }
    .faq-category-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }
    .faq-category-title::after {
        content: "";
        flex-grow: 1;
        height: 1px;
        background-color: #E5E7EB;
        margin-left: 1rem;
    }
    .faq-item {
        background-color: white;
        border-radius: 8px;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        overflow: hidden;
        border: 1px solid #E5E7EB;
    }
    .faq-question {
        padding: 1rem;
        font-weight: 500;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .faq-answer {
        padding: 0 1rem 1rem 1rem;
        border-top: 1px solid #E5E7EB;
        background-color: #F9FAFB;
    }
    
    /* Hide or blend Streamlit's iframe resizer elements */
    [data-testid="IframeResizerAnchor"] {
        display: none !important;
    }
    
    /* Hide the blue bar element */
    .st-emotion-cache-1dumvfu {
        display: none !important;
    }    /* Additional iframe and resizer element hiding */
    div[data-iframe-height="true"] {
        display: none !important;
    }
    
    /* General cleanup of Streamlit UI elements that might interfere */
    .st-emotion-cache-13k62yr {
        background: transparent !important;
    }    /* Custom State Card Expander Styling */
    .streamlit-expanderHeader {
        background: linear-gradient(145deg, #1e293b 0%, #334155 100%);
        border: 1px solid #475569;
        border-radius: 5px;
        color: #e2e8f0 !important;
        font-size: 0.85rem;
        padding: 0.3rem 0.8rem;
    }
    
    .streamlit-expanderContent {
        background: #1e293b;
        border: 1px solid #475569;
        border-radius: 0 0 5px 5px;
        padding: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)


class DashboardData:
    """Handles data loading and processing for the dashboard."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_path = self.project_root / "data"
        self.azure_openai = AzureOpenAIService()
        self.store_summaries_cache = {}  # Cache for store summaries
        self.qa_cache = {}  # Cache for Q&A responses
        self.last_refresh = datetime.now()

    def load_williams_sonoma_data(self) -> Dict[str, Any]:
        """Load real Williams Sonoma data for authentic location experience."""
        try:
            # Load Williams Sonoma reviews
            try:
                with open(self.data_path / "williams_sonoma_reviews.json", 'r') as f:
                    reviews = json.load(f)
                    logger.info("Loaded Williams Sonoma reviews: %d entries", len(reviews))
            except FileNotFoundError:
                # Fallback to mock reviews if Williams Sonoma file not found
                with open(self.data_path / "mock_reviews.json", 'r') as f:
                    reviews = json.load(f)
                    logger.warning("Williams Sonoma reviews not found, using mock data")
              # Load Williams Sonoma store info
            try:
                with open(self.data_path / "williams_sonoma_stores.json", 'r') as f:
                    stores = json.load(f)
                    logger.info("Loaded Williams Sonoma stores: %d locations", len(stores))
                    
                    # Log the first 5 and last 5 store names to verify data
                    store_names_first = [store["name"] for store in stores[:5]]
                    store_names_last = [store["name"] for store in stores[-5:]]
                    logger.info(f"First 5 stores: {', '.join(store_names_first)}")
                    logger.info(f"Last 5 stores: {', '.join(store_names_last)}")
            except FileNotFoundError:
                # Fallback to mock store info if Williams Sonoma file not found
                with open(self.data_path / "mock_store_info.json", 'r') as f:
                    stores = json.load(f)
                    logger.warning("Williams Sonoma stores not found, using mock data")
              
            # Load Williams Sonoma Q&A data
            try:
                with open(self.data_path / "williams_sonoma_qna.json", 'r') as f:
                    qna = json.load(f)
                    logger.info("Loaded Williams Sonoma Q&A: %d entries", len(qna))
            except FileNotFoundError:
                # Fallback to mock Q&A data
                try:
                    with open(self.data_path / "mock_qna_extended.json", 'r') as f:
                        qna = json.load(f)
                        logger.warning("Williams Sonoma Q&A not found, using mock extended data")
                except FileNotFoundError:
                    with open(self.data_path / "mock_qna.json", 'r') as f:
                        qna = json.load(f)
                        logger.warning("Williams Sonoma Q&A not found, using mock data")
              # Update last refresh time
            self.last_refresh = datetime.now()
            
            return {
                "reviews": reviews,
                "stores": stores,
                "qna": qna
            }
        except Exception as e:
            st.error(f"Error loading Williams Sonoma data: {e}")
            return {"reviews": [], "stores": [], "qna": []}
            
    def generate_store_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate store-level insights from mock data."""
        insights = {}
        
        # Debug: Count the number of stores being processed
        total_stores = len(data["stores"])
        logger.info(f"Processing insights for {total_stores} stores")
        
        for store in data["stores"]:
            store_id = store["store_id"]
            store_reviews = [r for r in data["reviews"] if r["store_id"] == store_id]
            
            # Include all stores even if they don't have reviews
            # Default values for stores without reviews
            if not store_reviews:
                avg_rating = 0.0
                total_reviews = 0
                positive_reviews = 0
                negative_reviews = 0
                ratings = []
                all_text = ""
                logger.debug(f"Store {store_id} has no reviews")
            else:
                # Calculate metrics
                ratings = [r["rating"] for r in store_reviews]
                avg_rating = sum(ratings) / len(ratings)
                total_reviews = len(store_reviews)
                
                # Simple sentiment analysis
                positive_reviews = len([r for r in store_reviews if r["rating"] >= 4])
                negative_reviews = len([r for r in store_reviews if r["rating"] <= 2])
                all_text = " ".join([r["text"].lower() for r in store_reviews])
                logger.debug(f"Store {store_id} has {total_reviews} reviews")
              # Extract common themes (simple keyword extraction)
            common_words = ["service", "staff", "quality", "price", "experience", 
                          "product", "store", "customer", "helpful", "clean"]
            themes = []
            for word in common_words:
                if all_text and word in all_text and all_text.count(word) >= 2:
                    themes.append({
                        "theme": word.title(),
                        "frequency": all_text.count(word),
                        "sentiment": "positive" if word in ["helpful", "quality", "clean"] else "neutral"
                    })
            
            # Calculate historical metrics (simulated)
            previous_avg_rating = avg_rating - random.uniform(-0.3, 0.3)
            previous_avg_rating = max(1.0, min(5.0, previous_avg_rating))  # Keep within 1-5 range
            rating_trend = avg_rating - previous_avg_rating
              # Calculate review volume trend (simulated)
            previous_review_count = int(total_reviews * random.uniform(0.8, 0.95))
            volume_trend = total_reviews - previous_review_count
            
            # Extract location information for Williams Sonoma stores
            location_city = store.get("address", "").split(",")[-2].strip() if "," in store.get("address", "") else "Unknown"
            location_state = store.get("address", "").split(",")[-1].strip().split()[0] if "," in store.get("address", "") else "Unknown"
            
            # Enhanced insights with Williams Sonoma specific data
            insights[store_id] = {
                "store_info": store,
                "avg_rating": avg_rating,
                "previous_avg_rating": previous_avg_rating,
                "rating_trend": rating_trend,
                "total_reviews": total_reviews,
                "previous_review_count": previous_review_count,
                "volume_trend": volume_trend,
                "positive_reviews": positive_reviews,
                "negative_reviews": negative_reviews,
                "sentiment_score": (positive_reviews - negative_reviews) / total_reviews if total_reviews > 0 else 0,
                "themes": themes[:5],  # Top 5 themes
                "latest_reviews": sorted(store_reviews, key=lambda x: x["date"], reverse=True)[:3],
                # Williams Sonoma specific attributes
                "location_city": location_city,
                "location_state": location_state,
                "manager": store.get("manager", "N/A"),
                "phone": store.get("phone", "N/A"),
                "square_footage": store.get("square_footage", 0),
                "employee_count": store.get("employee_count", 0),
                "services": store.get("services", []),
                "store_number": store.get("store_number", "N/A"),
                "opening_date": store.get("opening_date", "N/A")
            }
        
        return insights
            
    def generate_executive_summary(self, store_insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary from store insights."""
        if not store_insights:
            return {}
        
        # Count the total number of stores from the store insights
        total_stores = len(store_insights)
        logger.info(f"Executive summary calculating metrics for {total_stores} stores")
        
        all_ratings = [insight["avg_rating"] for insight in store_insights.values() if insight["total_reviews"] > 0]
        all_reviews = sum([insight["total_reviews"] for insight in store_insights.values()])
        
        # Calculate trends
        all_rating_trends = [insight["rating_trend"] for insight in store_insights.values()]
        all_volume_trends = [insight["volume_trend"] for insight in store_insights.values()]
          # Calculate overall metrics only for stores with reviews
        overall_avg_rating = sum(all_ratings) / len(all_ratings) if all_ratings else 0
        overall_rating_trend = sum(all_rating_trends) / len(all_rating_trends) if all_rating_trends else 0
        overall_volume_trend = sum(all_volume_trends)
        
        # Log the number of stores with ratings vs. total
        stores_with_ratings = len([i for i in store_insights.values() if i["total_reviews"] > 0])
        logger.info(f"Stores with ratings: {stores_with_ratings} out of {total_stores} total stores")
        
        # Performance categories
        top_performers = [
            (store_id, insight) for store_id, insight in store_insights.items()
            if insight["avg_rating"] >= 4.0
        ]
        
        underperformers = [
            (store_id, insight) for store_id, insight in store_insights.items()
            if insight["avg_rating"] < 3.0
        ]
        
        # Most improved and declined
        most_improved = sorted(
            [(store_id, insight) for store_id, insight in store_insights.items()],
            key=lambda x: x[1]["rating_trend"],
            reverse=True
        )[:3]
        
        most_declined = sorted(
            [(store_id, insight) for store_id, insight in store_insights.items()],
            key=lambda x: x[1]["rating_trend"]
        )[:3]
        
        # Generate alerts
        alerts = []
        for store_id, insight in store_insights.items():
            store_name = insight["store_info"]["name"]
            
            if insight["avg_rating"] < 2.5:
                alerts.append({
                    "severity": "high",
                    "message": f"{store_name} has critically low rating ({insight['avg_rating']:.1f})",
                    "store_id": store_id
                })
            elif insight["negative_reviews"] > insight["positive_reviews"]:
                alerts.append({
                    "severity": "medium", 
                    "message": f"{store_name} has more negative than positive reviews",
                    "store_id": store_id
                })
            elif insight["rating_trend"] < -0.5:
                alerts.append({
                    "severity": "medium",
                    "message": f"{store_name} rating dropped by {abs(insight['rating_trend']):.1f} points",
                    "store_id": store_id
                })
        
        return {
            "total_stores": total_stores,
            "overall_avg_rating": overall_avg_rating,
            "overall_rating_trend": overall_rating_trend,
            "total_reviews": all_reviews,
            "review_volume_trend": overall_volume_trend,
            "top_performers": top_performers,
            "underperformers": underperformers,
            "most_improved": most_improved,
            "most_declined": most_declined,
            "alerts": alerts,
            "last_updated": self.last_refresh.isoformat()
        }
    
    def check_server_status(self, server_type: str) -> Dict[str, Any]:
        """Check the status of MCP servers.
        
        In a real implementation, this would make API calls to the servers.
        """
        current_time = datetime.now()
        
        # Simulate different statuses based on server type
        if server_type == "collection":
            # In real implementation, this would make a health check request to the collection server
            return {
                "status": "Online",
                "last_activity": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "health": "Good",
                "api_calls_today": 127,
                "stores_processed": 15,
                "recent_activity": [
                    {"time": (current_time - timedelta(minutes=5)).strftime("%H:%M:%S"), "action": "Fetched reviews for Store #103"},
                    {"time": (current_time - timedelta(minutes=12)).strftime("%H:%M:%S"), "action": "Processed 32 new customer reviews"},
                    {"time": (current_time - timedelta(minutes=25)).strftime("%H:%M:%S"), "action": "Fetched store data for 5 locations"}
                ]
            }
        elif server_type == "aggregation":
            # In real implementation, this would make a health check request to the aggregation server
            return {
                "status": "Online",
                "last_activity": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "health": "Good",
                "insights_processed": 32,
                "alerts_generated": 5,
                "recent_activity": [
                    {"time": (current_time - timedelta(minutes=8)).strftime("%H:%M:%S"), "action": "Generated executive summary"},
                    {"time": (current_time - timedelta(minutes=15)).strftime("%H:%M:%S"), "action": "Identified 2 trending issues"},
                    {"time": (current_time - timedelta(minutes=30)).strftime("%H:%M:%S"), "action": "Created store insights for 15 locations"}
                ]
            }
        else:
            return {
                "status": "Unknown",
                "last_activity": "N/A",
                "health": "Unknown",
                "recent_activity": []
            }
    
    def get_store_summary(self, store_insight: Dict[str, Any]) -> Dict[str, Any]:
        """Get an AI-generated summary of the store status."""
        store_id = store_insight.get("store_info", {}).get("store_id")
        
        # Check cache first
        if store_id in self.store_summaries_cache:
            return self.store_summaries_cache[store_id]
          # Generate new summary with Azure OpenAI
        summary = self.azure_openai.generate_store_summary(store_insight)
        
        # Cache the result
        if store_id:
            self.store_summaries_cache[store_id] = summary
            
        return summary
    
    def ask_store_question(self, store_insight: Dict[str, Any], question: str) -> str:
        """Ask a question about a specific store."""
        if not question.strip():
            return "Please ask a specific question about this store."
        
        store_id = store_insight.get("store_info", {}).get("store_id")
        cache_key = f"{store_id}:{question}"
        
        # Check cache first
        if cache_key in self.qa_cache:
            return self.qa_cache[cache_key]
              # Get answer from Azure OpenAI
        answer = self.azure_openai.answer_store_question(store_insight, question)
        
        # Cache the result
        self.qa_cache[cache_key] = answer
        return answer
    
    def format_rating_stars(self, rating: float) -> str:
        """Format a rating as HTML stars."""
        full_stars = int(rating)
        half_star = rating - full_stars >= 0.5
        empty_stars = 5 - full_stars - (1 if half_star else 0)
        
        stars_html = ""
        stars_html += '<span class="star-filled">★</span>' * full_stars
        if half_star:
            stars_html += '<span class="star-filled">★</span>'
        stars_html += '<span class="star-empty">★</span>' * empty_stars
        
        return f'<div class="rating-display">{stars_html} <span style="margin-left: 0.5rem;">{rating:.1f}</span></div>'
    
    def format_trend_indicator(self, trend: float) -> str:
        """Format a trend value as an HTML indicator."""
        if trend > 0:
            return f'<span class="trend-up">▲ {trend:.2f}</span>'
        elif trend < 0:
            return f'<span class="trend-down">▼ {abs(trend):.2f}</span>'
        else:
            return '<span style="color: #6B7280;">◆ 0.00</span>'
    
    def get_store_kpis(self, store_insight: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get KPIs for a store in a format ready for display."""
        kpis = [
            {
                "title": "Average Rating",
                "value": f"{store_insight['avg_rating']:.1f}",
                "trend": store_insight['rating_trend'],
                "trend_text": f"{'+' if store_insight['rating_trend'] >= 0 else ''}{store_insight['rating_trend']:.2f} pts",
                "icon": "⭐"
            },
            {
                "title": "Total Reviews",
                "value": str(store_insight['total_reviews']),
                "trend": store_insight['volume_trend'],
                "trend_text": f"+{store_insight['volume_trend']}" if store_insight['volume_trend'] > 0 else str(store_insight['volume_trend']),
                "icon": "📝"
            },
            {
                "title": "Positive Reviews",
                "value": str(store_insight['positive_reviews']),
                "trend": None,
                "trend_text": f"{int(100 * store_insight['positive_reviews'] / store_insight['total_reviews'])}%" if store_insight['total_reviews'] > 0 else "N/A",
                "icon": "👍"
            },
            {
                "title": "Negative Reviews",
                "value": str(store_insight['negative_reviews']),
                "trend": None,
                "trend_text": f"{int(100 * store_insight['negative_reviews'] / store_insight['total_reviews'])}%" if store_insight['total_reviews'] > 0 else "N/A",
                "icon": "👎"
            },
            {
                "title": "Sentiment Score",
                "value": f"{store_insight['sentiment_score']:.2f}",
                "trend": None,
                "trend_text": "Positive" if store_insight['sentiment_score'] > 0.2 else "Neutral" if store_insight['sentiment_score'] >= -0.2 else "Negative",
                "icon": "📊"
            }
        ]
        return kpis
    
    def get_store_faqs(self, store_id: str, data: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Get categorized FAQs for a specific store.
        
        Args:
            store_id: The store ID to filter questions for
            data: The full data dictionary with qna data
            
        Returns:
            Dictionary with categories as keys and lists of Q&A items as values
        """
        try:
            # Load question categories
            categories_map = {}
            try:
                with open(self.data_path / "question_categories.json", 'r') as f:
                    categories_map = json.load(f)
                logger.info("Loaded %d question categories", len(categories_map))
            except FileNotFoundError:
                logger.warning("Question categories file not found, using raw categories")
            
            # Filter Q&A for this store
            store_qna = [q for q in data["qna"] if q["store_id"] == store_id]
            
            # Group by category
            categorized_qna = {}
            for qa_item in store_qna:
                category = qa_item.get("category", "uncategorized")
                # Use friendly category name if available
                try:
                    display_category = categories_map.get(category, category.title())
                    # Ensure display_category is a string
                    if not isinstance(display_category, str):
                        display_category = str(category).title()
                except Exception:
                    display_category = str(category).title()
                if display_category not in categorized_qna:
                    categorized_qna[display_category] = []
                
                categorized_qna[display_category].append(qa_item)
            
            # Sort each category by date (newest first)
            for category, items in categorized_qna.items():
                categorized_qna[category] = sorted(
                    items,
                    key=lambda x: x.get("date", "2000-01-01"),
                    reverse=True
                )
              # Sort categories by number of questions (most first)
            sorted_categories = {}
            for category in sorted(categorized_qna.keys(), 
                                  key=lambda x: len(categorized_qna[x]),
                                  reverse=True):
                sorted_categories[category] = categorized_qna[category]
            
            return sorted_categories
        except Exception as e:
            logger.error(f"Error getting store FAQs: {e}")
            return {}


# Helper function to extract coordinates from store data
def get_store_coordinates():
    """Get approximate coordinates for Williams Sonoma stores based on their locations."""
    # This is a simplified mapping - in production you'd use a geocoding service
    coordinates = {
        "ws_001": {"lat": 39.1157, "lon": -77.5636, "city": "Leesburg", "state": "VA"},
        "ws_002": {"lat": 38.8618, "lon": -77.3569, "city": "Fairfax", "state": "VA"},
        "ws_003": {"lat": 38.8618, "lon": -77.3569, "city": "Fairfax", "state": "VA"},
        "ws_004": {"lat": 30.6954, "lon": -88.0399, "city": "Mobile", "state": "AL"},
        "ws_005": {"lat": 32.7767, "lon": -96.7970, "city": "Dallas", "state": "TX"},
        "ws_006": {"lat": 30.2672, "lon": -97.7431, "city": "Austin", "state": "TX"},
        "ws_007": {"lat": 29.7604, "lon": -95.3698, "city": "Houston", "state": "TX"},
        "ws_008": {"lat": 34.0522, "lon": -118.2437, "city": "Los Angeles", "state": "CA"},
        "ws_009": {"lat": 37.7749, "lon": -122.4194, "city": "San Francisco", "state": "CA"},
        "ws_010": {"lat": 32.7157, "lon": -117.1611, "city": "San Diego", "state": "CA"},
        "ws_011": {"lat": 28.3702, "lon": -81.5182, "city": "Orlando", "state": "FL"},
        "ws_012": {"lat": 37.4436, "lon": -122.1713, "city": "Palo Alto", "state": "CA"},
        "ws_013": {"lat": 34.0722, "lon": -118.3572, "city": "Los Angeles", "state": "CA"},        "ws_014": {"lat": 41.9103, "lon": -87.6496, "city": "Chicago", "state": "IL"},
        "ws_015": {"lat": 40.0886, "lon": -75.3941, "city": "King of Prussia", "state": "PA"},
        "ws_016": {"lat": 40.7243, "lon": -74.3279, "city": "Short Hills", "state": "NJ"},
        "ws_017": {"lat": 39.7175, "lon": -104.9536, "city": "Denver", "state": "CO"},
        "ws_018": {"lat": 47.6164, "lon": -122.2019, "city": "Bellevue", "state": "WA"},
        "ws_019": {"lat": 33.8461, "lon": -84.3633, "city": "Atlanta", "state": "GA"},
        "ws_020": {"lat": 28.4856, "lon": -81.4309, "city": "Orlando", "state": "FL"},
        "ws_021": {"lat": 32.9307, "lon": -96.8197, "city": "Dallas", "state": "TX"},
        "ws_022": {"lat": 33.5022, "lon": -111.9286, "city": "Scottsdale", "state": "AZ"},
        "ws_023": {"lat": 32.7698, "lon": -117.1664, "city": "San Diego", "state": "CA"},
        "ws_024": {"lat": 38.9174, "lon": -77.2198, "city": "Tysons", "state": "VA"},
        "ws_025": {"lat": 32.8679, "lon": -96.7738, "city": "Dallas", "state": "TX"},
    }
    return coordinates

def create_store_map(store_insights):
    """Create an interactive map with store locations and insights."""
    coordinates = get_store_coordinates()
    
    # Prepare data for the map
    map_data = []
    for store_id, insight in store_insights.items():
        if store_id in coordinates:
            coord = coordinates[store_id]
            store_info = insight["store_info"]
              # Create hover text with store details
            hover_text = f"""
            <b style='font-size: 14px; color: #f8fafc;'>{store_info['name']}</b><br>
            <span style='color: #94a3b8;'>📍 {coord['city']}, {coord['state']}</span><br>
            <span style='color: {"#10B981" if insight["avg_rating"] >= 4.0 else "#F59E0B" if insight["avg_rating"] >= 3.5 else "#EF4444"};'>
                ⭐ Rating: {insight['avg_rating']:.1f}/5
            </span><br>
            💬 Reviews: {insight['total_reviews']}<br>
            👥 Manager: {store_info.get('manager', 'N/A')}<br>
            📞 {store_info.get('phone', 'N/A')}<br>
            🏪 Size: {store_info.get('square_footage', 'N/A')} sq ft
            """
            
            map_data.append({
                "lat": coord["lat"],
                "lon": coord["lon"],
                "store_name": store_info["name"],
                "city": coord["city"],
                "state": coord["state"],
                "rating": insight["avg_rating"],
                "reviews": insight["total_reviews"],
                "manager": store_info.get("manager", "N/A"),
                "phone": store_info.get("phone", "N/A"),
                "size": store_info.get("square_footage", "N/A"),                "hover_text": hover_text,
                "marker_color": "#10B981" if insight["avg_rating"] >= 4.0 else 
                               "#F59E0B" if insight["avg_rating"] >= 3.5 else 
                               "#EF4444"
            })
    
    if not map_data:
        return None
    # Create the map
    fig = go.Figure()
      # Add US state boundaries with subtle styling
    fig.add_trace(go.Choropleth(
        locations=["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", 
                  "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
                  "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
                  "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
                  "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"],
        locationmode="USA-states",
        z=[1] * 50,  # Same value for all states for even coloring
        colorscale=[[0, "#1e293b"], [1, "#334155"]],  # Dark theme gradient
        showscale=False,
        marker=dict(line=dict(color="#475569", width=0.5)),  # Subtle state borders
        hoverinfo="skip",
        showlegend=False
    ))    # Add store markers with improved styling
    fig.add_trace(go.Scattergeo(
        lat=[d["lat"] for d in map_data],
        lon=[d["lon"] for d in map_data],
        mode='markers+text',
        marker=dict(
            size=14,
            color=[d["marker_color"] for d in map_data],
            opacity=0.9,
            symbol="circle",
            line=dict(width=1.5, color="#E2E8F0"),  # Light border for contrast
            gradient=dict(type="radial", color="#FFFFFF"),  # Subtle radial gradient
            sizemode="diameter"
        ),
        text=[d["store_name"] if d["rating"] >= 4.3 else "" for d in map_data],  # Only show names for top stores
        textposition="top center",
        textfont=dict(family="Arial", size=10, color="#f1f5f9"),
        hovertext=[d["hover_text"] for d in map_data],
        hovertemplate='%{hovertext}<extra></extra>',
        hoverlabel=dict(
            bgcolor="#1e293b",
            bordercolor="#475569",
            font=dict(family="Arial", size=12, color="#f1f5f9")
        ),
        name="Williams Sonoma Stores"
    ))
      # Add a custom legend
    high_performers = len([d for d in map_data if d["rating"] >= 4.0])
    average_performers = len([d for d in map_data if 3.5 <= d["rating"] < 4.0])
    low_performers = len([d for d in map_data if d["rating"] < 3.5])
    
    # Add annotations for the legend
    fig.add_annotation(
        x=0.01, y=0.16,
        xref="paper", yref="paper",
        text=f"<b>Store Ratings</b><br><span style='color:#10B981'>⬤</span> High (4.0+): {high_performers}<br>" +
             f"<span style='color:#F59E0B'>⬤</span> Average (3.5-3.9): {average_performers}<br>" +
             f"<span style='color:#EF4444'>⬤</span> Low (<3.5): {low_performers}",
        align="left",
        showarrow=False,
        bgcolor="rgba(15,23,42,0.8)",
        bordercolor="#475569",
        borderwidth=1,
        borderpad=6,
        font=dict(color="#f1f5f9", size=10)
    )
    
    # Update layout with improved styling
    fig.update_layout(
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="#1e293b",
            showocean=True,
            oceancolor="#0f172a",
            showlakes=True,
            lakecolor="#0f172a",
            showrivers=False,
            showcoastlines=True,
            coastlinecolor="#475569",
            showframe=False,
            framecolor="#475569",
            bgcolor="rgba(0,0,0,0)",
            showsubunits=True,
            subunitcolor="#475569",
            subunitwidth=0.5
        ),        height=600,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        title=dict(
            text="Williams Sonoma U.S. Store Network",
            font=dict(size=16, color="#f1f5f9", family="Arial"),
            x=0.5,
            y=0.98,
            xanchor="center",
            yanchor="top"
        ),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(15,23,42,0.7)",
            bordercolor="#475569",
            borderwidth=1,
            font=dict(color="#f1f5f9", size=10),
            orientation="v"
        )
    )
    
    return fig


def main():
    """Main dashboard function."""
    # Dashboard header with logo and title
    st.markdown(        """
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <div style="font-size: 2.5rem; margin-right: 0.5rem;">🏪</div>
            <div>
                <h1 style="margin: 0; padding: 0;">Williams Sonoma Business Analytics Dashboard</h1>
                <p style="margin: 0; padding: 0; color: #6B7280;">Powered by MCP Protocol</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize data handler
    data_handler = DashboardData()
    
    # Sidebar controls and server status
    with st.sidebar:
        st.header("Dashboard Controls")
        
        # Date range selector
        st.subheader("Date Range")
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
        with col2:
            end_date = st.date_input("End Date", value=datetime.now().date())
        
        # Refresh options
        st.subheader("Data Refresh")
        auto_refresh = st.checkbox("Auto-refresh (15s)", value=False)
        
        if st.button("🔄 Refresh Data Now", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        # Server Health Section
        st.markdown("---")
        st.header("MCP Server Status")
        
        # Check server statuses
        collection_server_status = data_handler.check_server_status("collection")
        aggregation_server_status = data_handler.check_server_status("aggregation")
        
        # Collection Server Tab
        tab1, tab2 = st.tabs(["Collection Agent", "Aggregation Agent"])
        
        with tab1:
            # Status indicator
            status_color = "status-online" if collection_server_status["status"] == "Online" else "status-offline"
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div class="status-indicator {status_color}"></div>
                <div style="font-weight: bold;">{collection_server_status["status"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # KPIs
            st.markdown(f"""
            <div class="metric-container" style="margin: 0.5rem 0; padding: 0.75rem;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <div style="font-size: 0.75rem; color: #6B7280;">API Calls Today</div>
                        <div style="font-size: 1.25rem; font-weight: bold;">{collection_server_status["api_calls_today"]}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #6B7280;">Stores Processed</div>
                        <div style="font-size: 1.25rem; font-weight: bold;">{collection_server_status["stores_processed"]}</div>
                    </div>
                </div>
                <div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.5rem;">
                    Last Activity: {collection_server_status["last_activity"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recent Activity
            st.markdown("##### Recent Activity")
            for activity in collection_server_status.get("recent_activity", []):
                st.markdown(f"""
                <div style="display: flex; padding: 0.3rem 0; border-bottom: 1px solid #E5E7EB;">
                    <div style="color: #6B7280; font-size: 0.75rem; width: 50px;">{activity["time"]}</div>
                    <div style="font-size: 0.8rem; margin-left: 0.5rem;">{activity["action"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        with tab2:
            # Status indicator
            status_color = "status-online" if aggregation_server_status["status"] == "Online" else "status-offline"
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <div class="status-indicator {status_color}"></div>
                <div style="font-weight: bold;">{aggregation_server_status["status"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # KPIs
            st.markdown(f"""
            <div class="metric-container" style="margin: 0.5rem 0; padding: 0.75rem;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <div style="font-size: 0.75rem; color: #6B7280;">Insights Processed</div>
                        <div style="font-size: 1.25rem; font-weight: bold;">{aggregation_server_status["insights_processed"]}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #6B7280;">Alerts Generated</div>
                        <div style="font-size: 1.25rem; font-weight: bold;">{aggregation_server_status["alerts_generated"]}</div>
                    </div>
                </div>
                <div style="font-size: 0.75rem; color: #6B7280; margin-top: 0.5rem;">
                    Last Activity: {aggregation_server_status["last_activity"]}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Recent Activity
            st.markdown("##### Recent Activity")
            for activity in aggregation_server_status.get("recent_activity", []):
                st.markdown(f"""
                <div style="display: flex; padding: 0.3rem 0; border-bottom: 1px solid #E5E7EB;">
                    <div style="color: #6B7280; font-size: 0.75rem; width: 50px;">{activity["time"]}</div>
                    <div style="font-size: 0.8rem; margin-left: 0.5rem;">{activity["action"]}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown(
            """
            <div style="text-align: center; font-size: 0.75rem; color: #6B7280; margin-top: 2rem;">
                Powered by Model Context Protocol<br>
                Version 1.0.0
            </div>
            """,
            unsafe_allow_html=True
        )
      # Load and process data
    with st.spinner("Loading Williams Sonoma data..."):
        mock_data = data_handler.load_williams_sonoma_data()
        # Debug: Log the number of stores in mock_data
        stores_count = len(mock_data['stores'])
        logger.info(f"DEBUG: Number of stores in mock_data: {stores_count}")
        
        store_insights = data_handler.generate_store_insights(mock_data)
        # Debug: Log the number of stores in store_insights
        insights_count = len(store_insights)
        logger.info(f"DEBUG: Number of stores in store_insights: {insights_count}")
        
        executive_summary = data_handler.generate_executive_summary(store_insights)
        # Debug: Log the total_stores in executive_summary
        exec_count = executive_summary['total_stores']
        logger.info(f"DEBUG: executive_summary total_stores: {exec_count}")
        
        # Display debug info in an expandable section
        with st.expander("Debug Information"):
            st.write(f"Number of stores in data file: {stores_count}")
            st.write(f"Number of stores with insights: {insights_count}")
            st.write(f"Total stores in executive summary: {exec_count}")
              # Count stores with/without reviews
            stores_with_reviews = 0
            for store_id, insight in store_insights.items():
                if insight["total_reviews"] > 0:
                    stores_with_reviews += 1
            
            st.write(f"Stores with reviews: {stores_with_reviews}")
            st.write(f"Stores without reviews: {insights_count - stores_with_reviews}")
            
            # List first 5 stores with reviews
            st.write("First 5 stores with reviews:")
            count = 0
            for store_id, insight in store_insights.items():
                if insight["total_reviews"] > 0 and count < 5:
                    st.write(f"{count+1}. {store_id} - {insight['store_info']['name']} ({insight['total_reviews']} reviews)")
                    count += 1
                    
            # List first 5 stores without reviews
            st.write("First 5 stores without reviews:")
            count = 0
            for store_id, insight in store_insights.items():
                if insight["total_reviews"] == 0 and count < 5:
                    st.write(f"{count+1}. {store_id} - {insight['store_info']['name']}")
                    count += 1
    
    if not executive_summary:
        st.error("No data available. Please check your data sources.")
        return
    
    # Main dashboard tabs
    overview_tab, store_details_tab, analytics_tab, faq_tab = st.tabs([
        "📊 Executive Overview", 
        "🏪 Store Details", 
        "🧠 AI-Powered Analytics",
        "❓ FAQ & Customer Questions"
    ])
    
    # Executive Overview Tab
    with overview_tab:
        # Key Metrics Row
        st.subheader("Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-container">
                <div style="font-size: 0.875rem; color: #6B7280;">Total Stores</div>
                <div style="font-size: 2rem; font-weight: bold; color: #1E40AF;">{}</div>
                <div style="font-size: 0.875rem; color: #6B7280; margin-top: 0.5rem;">Active Locations</div>
            </div>
            """.format(executive_summary["total_stores"]), unsafe_allow_html=True)
        
        with col2:
            trend_class = "trend-up" if executive_summary["overall_rating_trend"] >= 0 else "trend-down"
            trend_symbol = "▲" if executive_summary["overall_rating_trend"] >= 0 else "▼"
            trend_value = abs(executive_summary["overall_rating_trend"])
            
            st.markdown("""
            <div class="metric-container">
                <div style="font-size: 0.875rem; color: #6B7280;">Overall Rating</div>
                <div style="display: flex; align-items: baseline;">
                    <div style="font-size: 2rem; font-weight: bold; color: #1E40AF;">{:.1f}</div>
                    <div style="font-size: 1rem; margin-left: 0.5rem;">/5.0</div>
                </div>
                <div style="font-size: 0.875rem; margin-top: 0.5rem;">
                    <span class="{}">{} {:.2f}</span> from last period
                </div>
            </div>
            """.format(
                executive_summary["overall_avg_rating"], 
                trend_class, trend_symbol, trend_value
            ), unsafe_allow_html=True)
        
        with col3:
            volume_trend = executive_summary["review_volume_trend"]
            trend_class = "trend-up" if volume_trend >= 0 else "trend-down"
            trend_symbol = "▲" if volume_trend >= 0 else "▼"
            
            st.markdown("""
            <div class="metric-container">
                <div style="font-size: 0.875rem; color: #6B7280;">Total Reviews</div>
                <div style="font-size: 2rem; font-weight: bold; color: #1E40AF;">{}</div>
                <div style="font-size: 0.875rem; margin-top: 0.5rem;">
                    <span class="{}">{} {}</span> from last period
                </div>
            </div>
            """.format(
                executive_summary["total_reviews"], 
                trend_class, trend_symbol, abs(volume_trend)
            ), unsafe_allow_html=True)
        
        with col4:
            alerts_count = len(executive_summary["alerts"])
            alert_color = "#EF4444" if alerts_count > 0 else "#10B981"
            
            st.markdown("""
            <div class="metric-container">
                <div style="font-size: 0.875rem; color: #6B7280;">Active Alerts</div>
                <div style="font-size: 2rem; font-weight: bold; color: {};">{}</div>
                <div style="font-size: 0.875rem; color: #6B7280; margin-top: 0.5rem;">
                    {} high severity
                </div>
            </div>
            """.format(
                alert_color, 
                alerts_count,
                sum(1 for a in executive_summary["alerts"] if a["severity"] == "high")
            ), unsafe_allow_html=True)
        
        # Alerts Section
        if executive_summary["alerts"]:
            with st.expander("🚨 Active Alerts", expanded=True):
                for alert in executive_summary["alerts"]:
                    alert_class = f"alert-{alert['severity']}"
                    st.markdown(f"""
                    <div class="{alert_class}">
                        <strong>{alert['severity'].upper()}:</strong> {alert['message']}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Performance Overview
        st.subheader("Performance Overview")
        
        # Create rating distribution chart
        ratings_data = []
        for store_id, insight in store_insights.items():
            ratings_data.append({
                "Store": insight["store_info"]["name"],
                "Rating": insight["avg_rating"],
                "Previous Rating": insight["previous_avg_rating"],
                "Reviews": insight["total_reviews"],
                "Category": insight["store_info"]["category"],
                "Rating Change": insight["rating_trend"]
            })
        
        if ratings_data:
            # Convert to DataFrame
            df_ratings = pd.DataFrame(ratings_data)
            
            # Two charts side by side
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Average Rating by Store")
                # Sort by rating for better visualization
                df_sorted = df_ratings.sort_values("Rating", ascending=False)
                
                fig_ratings = px.bar(
                    df_sorted,
                    x="Store",
                    y="Rating",
                    color="Category",
                    hover_data=["Reviews", "Rating Change"],
                    color_discrete_sequence=px.colors.qualitative.Set3,
                    text="Rating"
                )
                fig_ratings.update_layout(
                    yaxis=dict(range=[0, 5.5]),
                    height=400,
                    margin=dict(t=20, b=20, l=20, r=20),
                )
                fig_ratings.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                st.plotly_chart(fig_ratings, use_container_width=True)
            
            with col2:
                st.markdown("##### Review Volume by Store")
                # Sort by review volume for better visualization
                df_sorted = df_ratings.sort_values("Reviews", ascending=False)
                
                fig_volume = px.bar(
                    df_sorted,
                    x="Store", 
                    y="Reviews",
                    color="Category",
                    text="Reviews",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig_volume.update_layout(
                    height=400,
                    margin=dict(t=20, b=20, l=20, r=20),
                )
                fig_volume.update_traces(textposition='outside')
                st.plotly_chart(fig_volume, use_container_width=True)
        
        # Performance Categories
        st.subheader("Performance Categories")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Top Performers")
            if executive_summary["top_performers"]:
                for i, (store_id, insight) in enumerate(executive_summary["top_performers"][:5], 1):
                    store_name = insight["store_info"]["name"]
                    rating = insight["avg_rating"]
                    reviews = insight["total_reviews"]                
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem; padding: 1rem; background: linear-gradient(145deg, #6B7280 0%, #9CA3AF 100%); border: 1px solid #9CA3AF; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">
                        <div style="font-size: 1.2rem; font-weight: bold; width: 30px; color: #374151;">{i}</div>
                        <div style="flex-grow: 1; margin-left: 1rem;">
                            <div style="font-weight: 600; color: #1F2937; font-size: 1rem;">{store_name}</div>
                            <div style="font-size: 0.85rem; color: #374151; margin-top: 0.25rem;">{reviews} reviews</div>
                        </div>
                        <div style="font-weight: bold; font-size: 1.3rem; color: #374151; background: rgba(55, 65, 81, 0.15); padding: 0.5rem; border-radius: 6px;">{rating:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No top performers to display.")
        
        with col2:
            st.markdown("##### Needs Improvement")
            if executive_summary["underperformers"]:
                for i, (store_id, insight) in enumerate(executive_summary["underperformers"][:5], 1):
                    store_name = insight["store_info"]["name"]
                    rating = insight["avg_rating"]
                    reviews = insight["total_reviews"]                
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem; padding: 1rem; background: linear-gradient(145deg, #374151 0%, #4B5563 100%); border: 1px solid #6B7280; border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">
                        <div style="font-size: 1.2rem; font-weight: bold; width: 30px; color: #F59E0B;">{i}</div>
                        <div style="flex-grow: 1; margin-left: 1rem;">
                            <div style="font-weight: 600; color: #F3F4F6; font-size: 1rem;">{store_name}</div>
                            <div style="font-size: 0.85rem; color: #D1D5DB; margin-top: 0.25rem;">{reviews} reviews</div>
                        </div>
                        <div style="font-weight: bold; font-size: 1.3rem; color: #F59E0B; background: rgba(245, 158, 11, 0.1); padding: 0.5rem; border-radius: 6px;">{rating:.1f}</div>
                    </div>                    """, unsafe_allow_html=True)
            else:
                st.write("No underperforming stores to display.")
          # Geographic Overview
        st.subheader("Geographic Performance Overview")
        
        # Calculate geographic insights
        geo_data = {}
        for store_id, insight in store_insights.items():
            state = insight.get("location_state", "Unknown")
            city = insight.get("location_city", "Unknown")
            
            if state not in geo_data:
                geo_data[state] = {"cities": set(), "avg_ratings": [], "total_reviews": 0, "stores": 0}
            
            geo_data[state]["cities"].add(city)
            geo_data[state]["avg_ratings"].append(insight["avg_rating"])
            geo_data[state]["total_reviews"] += insight["total_reviews"]
            geo_data[state]["stores"] += 1
        
        # Interactive Store Map
        if geo_data:
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #0f172a 0%, #1e293b 100%); 
                 border: 1px solid #475569; 
                 padding: 1.5rem; 
                 border-radius: 10px; 
                 margin: 1rem 0; 
                 box-shadow: 0 10px 25px rgba(0,0,0,0.2);">
                <h5 style="color: #f1f5f9; margin-bottom: 1rem; font-weight: 600;">
                    🗺️ Williams Sonoma Store Network
                </h5>
            </div>
            """, unsafe_allow_html=True)
              # Create and display the interactive map
            store_map = create_store_map(store_insights)
            if store_map:
                # Custom CSS for dark theme map container
                st.markdown("""
                <style>
                    .mapbox-container {
                        background-color: #0f172a !important;
                        border-radius: 8px !important;
                        overflow: hidden !important;
                        border: 1px solid #334155 !important;
                    }
                    .js-plotly-plot .plotly .mapboxgl-map {
                        border-radius: 8px !important;
                    }
                    .plotly-notifier {
                        display: none !important;
                    }
                </style>
                """, unsafe_allow_html=True)
                
                map_container = st.container()
                with map_container:
                    st.plotly_chart(store_map, use_container_width=True, config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'autoScale2d'],
                        'toImageButtonOptions': {
                            'format': 'png',
                            'filename': 'williams_sonoma_store_map',
                            'height': 600,
                            'width': 1200,
                            'scale': 2
                        }
                    })
            else:
                st.warning("Unable to generate store map. Displaying summary instead.")
                
            # Store network summary below the map
            st.markdown("<h6 style='color: #f1f5f9; margin-top: 1.5rem;'>State-by-State Overview</h6>", unsafe_allow_html=True)
            
            # Initialize state expander states if not present
            if "expanded_states" not in st.session_state:
                st.session_state.expanded_states = {}
            
            # Create a two-column layout for the state cards
            cols = st.columns(2)
            
            # Split the states into two groups for a balanced layout
            sorted_states = sorted(geo_data.items())
            half_point = len(sorted_states) // 2 + len(sorted_states) % 2
            
            for col_idx, states_group in enumerate([sorted_states[:half_point], sorted_states[half_point:]]):
                with cols[col_idx]:
                    for state, data in states_group:
                        # Initialize state's expansion status if not already set
                        if state not in st.session_state.expanded_states:
                            st.session_state.expanded_states[state] = False
                            
                        avg_rating = sum(data["avg_ratings"]) / len(data["avg_ratings"]) if data["avg_ratings"] else 0
                        cities_count = len(data["cities"])
                        
                        # Create a collapsible section for each state
                        with st.expander(f"**{state}**", expanded=st.session_state.expanded_states[state]):
                            # Update expanded state
                            st.session_state.expanded_states[state] = True
                            
                            st.markdown(f"""
                            <div style="background: #374151; padding: 1rem; border-radius: 8px; margin-top: 0.5rem;">
                                <div style="color: #d1d5db; font-size: 0.9rem; margin-bottom: 0.25rem;">
                                    🏪 {data["stores"]} stores across {cities_count} cities
                                </div>
                                <div style="color: #d1d5db; font-size: 0.9rem; margin-bottom: 0.25rem;">
                                    ⭐ {avg_rating:.2f} avg rating
                                </div>
                                <div style="color: #d1d5db; font-size: 0.9rem;">
                                    💬 {data["total_reviews"]} total reviews
                                </div>
                            </div>
                            """, unsafe_allow_html=True)                            # List the stores in this state
                            stores_in_state = [
                                (store_id, insight["store_info"]["name"], insight["avg_rating"], insight["total_reviews"])
                                for store_id, insight in store_insights.items()
                                if insight["location_state"] == state
                            ]
                            
                            if stores_in_state:
                                st.markdown("<div style='margin-top: 0.75rem; font-size: 0.9rem; font-weight: bold;'>Stores in this state:</div>", unsafe_allow_html=True)
                                for store_id, name, rating, reviews in sorted(stores_in_state, key=lambda x: x[1]):
                                    st.markdown(f"""
                                    <div style="padding: 0.5rem 0; border-bottom: 1px solid #475569;">
                                        <div style="font-weight: bold;">{name}</div>
                                        <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                                            <span>⭐ {rating:.1f}/5.0</span>
                                            <span>{reviews} reviews</span>
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Trend Analysis
        st.subheader("Trend Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Most Improved")
            if executive_summary["most_improved"]:
                for i, (store_id, insight) in enumerate(executive_summary["most_improved"][:5], 1):
                    store_name = insight["store_info"]["name"]
                    rating = insight["avg_rating"]
                    trend = insight["rating_trend"]
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem; padding: 0.75rem; background: linear-gradient(135deg, #374151 0%, #4b5563 100%); border-radius: 10px; border-left: 4px solid #6b7280; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                        <div style="font-size: 1rem; font-weight: bold; width: 25px; color: #d1d5db;">{i}</div>
                        <div style="flex-grow: 1; margin-left: 0.5rem;">
                            <div style="font-weight: 500; color: #f3f4f6;">{store_name}</div>
                            <div style="font-size: 0.8rem; color: #9ca3af;">Current: {rating:.1f}</div>
                        </div>
                        <div style="font-weight: bold; font-size: 1.1rem; color: #d1d5db;">+{trend:.2f}</div>                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No improvement data to display.")
        
        with col2:
            st.markdown("##### Declining Ratings")
            if executive_summary["most_declined"]:
                for i, (store_id, insight) in enumerate(executive_summary["most_declined"][:5], 1):
                    store_name = insight["store_info"]["name"]
                    rating = insight["avg_rating"]
                    trend = insight["rating_trend"]
                    
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem; padding: 0.75rem; background: linear-gradient(135deg, #374151 0%, #4b5563 100%); border-radius: 10px; border-left: 4px solid #6b7280; box-shadow: 0 2px 8px rgba(0,0,0,0.3);">
                        <div style="font-size: 1rem; font-weight: bold; width: 25px; color: #d1d5db;">{i}</div>
                        <div style="flex-grow: 1; margin-left: 0.5rem;">
                            <div style="font-weight: 500; color: #f3f4f6;">{store_name}</div>
                            <div style="font-size: 0.8rem; color: #9ca3af;">Current: {rating:.1f}</div>
                        </div>
                        <div style="font-weight: bold; font-size: 1.1rem; color: #d1d5db;">{trend:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("No decline data to display.")
        
        # Last updated timestamp
        last_updated_time = datetime.fromisoformat(executive_summary["last_updated"])
        st.markdown(f"""
        <div style="text-align: right; font-size: 0.8rem; color: #6B7280; margin-top: 1rem;">
            Last updated: {last_updated_time.strftime("%Y-%m-%d %H:%M:%S")}
        </div>
        """, unsafe_allow_html=True)
    
    # Store Details Tab
    with store_details_tab:
        # Store selector
        st.subheader("Store Information")
        
        store_options = {insight["store_info"]["name"]: store_id 
                        for store_id, insight in store_insights.items()}
        
        selected_store_name = st.selectbox("Select Store", list(store_options.keys()))
        selected_store_id = store_options[selected_store_name]
        selected_insight = store_insights[selected_store_id]
        
        # Store overview
        store_info = selected_insight["store_info"]
          # Store header with rating and location details
        st.markdown(f"""
        <div style="display: flex; align-items: flex-start; margin: 1rem 0 2rem 0;">
            <div style="flex: 3; background: linear-gradient(145deg, #1e293b 0%, #334155 100%); border: 1px solid #475569; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); margin-right: 1rem;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 2rem; margin-right: 1rem;">🏪</div>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 600; color: #f1f5f9;">{store_info["name"]}</div>
                        <div style="color: #94a3b8; margin: 0.5rem 0;">{store_info["category"]} • Store {selected_insight.get("store_number", "N/A")}</div>
                        <div style="color: #94a3b8; font-size: 0.9rem;">{store_info["address"]}</div>
                    </div>
                </div>
                <div style="display: flex; margin-top: 1.5rem; flex-wrap: wrap;">
                    <div style="margin-right: 2rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.8rem; color: #6B7280;">Manager</div>
                        <div style="color: #e2e8f0;">{selected_insight.get("manager", "N/A")}</div>
                    </div>
                    <div style="margin-right: 2rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.8rem; color: #6B7280;">Phone</div>
                        <div style="color: #e2e8f0;">{selected_insight.get("phone", "N/A")}</div>
                    </div>
                    <div style="margin-right: 2rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.8rem; color: #6B7280;">Location</div>
                        <div style="color: #e2e8f0;">{selected_insight.get("location_city", "Unknown")}, {selected_insight.get("location_state", "Unknown")}</div>
                    </div>
                    <div style="margin-right: 2rem; margin-bottom: 1rem;">
                        <div style="font-size: 0.8rem; color: #6B7280;">Store Size</div>
                        <div style="color: #e2e8f0;">{selected_insight.get("square_footage", 0):,} sq ft</div>
                    </div>
                    <div>
                        <div style="font-size: 0.8rem; color: #6B7280;">Staff</div>
                        <div style="color: #e2e8f0;">{selected_insight.get("employee_count", 0)} employees</div>
                    </div>
                </div>
                <div style="margin-top: 1rem;">
                    <div style="font-size: 0.8rem; color: #6B7280; margin-bottom: 0.5rem;">Services Offered</div>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        {" ".join([f'<span style="background: #059669; color: white; padding: 0.25rem 0.75rem; border-radius: 15px; font-size: 0.75rem;">{service}</span>' for service in selected_insight.get("services", [])])}
                    </div>
                </div>
            </div>
            <div style="flex: 1; background: linear-gradient(145deg, #1e293b 0%, #334155 100%); border: 1px solid #475569; padding: 1.5rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3); text-align: center;">
                <div style="font-size: 0.8rem; color: #6B7280; margin-bottom: 0.5rem;">OVERALL RATING</div>
                <div style="font-size: 3rem; font-weight: bold; color: #3B82F6;">{selected_insight["avg_rating"]:.1f}</div>
                <div style="margin: 0.5rem 0;">
                    {data_handler.format_rating_stars(selected_insight["avg_rating"])}
                </div>
                <div style="font-size: 0.9rem; color: #e2e8f0;">
                    {data_handler.format_trend_indicator(selected_insight["rating_trend"])} from last period
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #475569;">
                    <div style="font-size: 0.8rem; color: #6B7280;">Opening Date</div>
                    <div style="color: #e2e8f0; font-size: 0.9rem;">{selected_insight.get("opening_date", "N/A")}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Store performance metrics
        st.markdown("##### Performance Metrics")
        
        # Get KPIs for the selected store
        kpis = data_handler.get_store_kpis(selected_insight)
        
        # Display KPIs in a row
        kpi_cols = st.columns(len(kpis))
        for i, kpi in enumerate(kpis):
            with kpi_cols[i]:
                trend_html = ""
                if kpi["trend"] is not None:
                    trend_class = "trend-up" if kpi["trend"] > 0 else "trend-down" if kpi["trend"] < 0 else ""
                    trend_html = f'<div class="kpi-trend {trend_class}">{kpi["trend_text"]}</div>'
                
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-title">{kpi["icon"]} {kpi["title"]}</div>
                    <div class="kpi-value">{kpi["value"]}</div>
                    {trend_html}
                </div>
                """, unsafe_allow_html=True)
        
        # Theme analysis and latest reviews
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### Common Themes")
            if selected_insight["themes"]:
                themes_df = pd.DataFrame(selected_insight["themes"])
                fig_themes = px.bar(
                    themes_df,
                    x="frequency",
                    y="theme",
                    orientation="h",
                    color="sentiment",
                    title="Most Mentioned Themes",
                    color_discrete_map={
                        "positive": "#10B981", 
                        "neutral": "#6B7280", 
                        "negative": "#EF4444"
                    },
                    height=300
                )
                fig_themes.update_layout(
                    margin=dict(t=30, b=0, l=0, r=0),
                    xaxis_title=None,
                    yaxis_title=None
                )
                st.plotly_chart(fig_themes, use_container_width=True)
            else:
                st.write("No themes identified yet.")
        
        with col2:
            st.markdown("##### Latest Reviews")
            
            for review in selected_insight["latest_reviews"]:
                rating_stars = "★" * int(review["rating"]) + "☆" * (5 - int(review["rating"]))
                rating_color = "#10B981" if review["rating"] >= 4 else "#F59E0B" if review["rating"] >= 3 else "#EF4444"                
                st.markdown(f"""
                <div style="padding: 0.75rem; background: linear-gradient(145deg, #6B7280 0%, #9CA3AF 100%); border-radius: 8px; margin-bottom: 0.75rem; border: 1px solid #9CA3AF; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="font-weight: 500; color: #1E40AF;">{review["reviewer_name"]}</div>
                        <div style="color: {rating_color}; font-weight: 500;">{rating_stars}</div>
                    </div>
                    <div style="margin: 0.5rem 0; font-size: 0.9rem; color: #374151;">"{review["text"][:150]}..."</div>
                    <div style="font-size: 0.8rem; color: #4B5563;">{review["date"][:10]}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # AI-Powered Analytics Tab
    with analytics_tab:
        st.subheader("AI-Powered Store Analysis")
        
        # Store selector for AI analysis
        store_options = {insight["store_info"]["name"]: store_id 
                        for store_id, insight in store_insights.items()}
        
        if "selected_store_for_ai" not in st.session_state:
            st.session_state.selected_store_for_ai = list(store_options.keys())[0]
        
        selected_store_name = st.selectbox(
            "Select Store for AI Analysis", 
            list(store_options.keys()),
            key="ai_store_selector"
        )
        selected_store_id = store_options[selected_store_name]
        selected_insight = store_insights[selected_store_id]
          # Run functions to get store summary
        @st.cache_data(ttl=300)  # Cache for 5 minutes
        def get_store_summary_cached(store_id):
            return data_handler.get_store_summary(store_insights[store_id])
          # Display a progress message while generating summary
        with st.spinner(f"Analyzing {selected_store_name} data..."):
            store_summary = get_store_summary_cached(selected_store_id)
        
        # Display store summary in an AI section
        st.markdown("""
        <div class="ai-section">
            <h3>AI-Generated Store Summary</h3>
            <div style="margin-top: 1rem;">
        """, unsafe_allow_html=True)
        
        # Display the entire store summary as it's a string, not a dictionary
        st.markdown(store_summary)
        
        # Close the HTML div
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Location-Based Analytics Section
        st.markdown("---")
        st.subheader("📍 Location-Based Analytics")
        
        # Create location performance comparison
        location_data = []
        state_performance = {}
        city_performance = {}
        
        for store_id, insight in store_insights.items():
            state = insight.get("location_state", "Unknown")
            city = insight.get("location_city", "Unknown")
            
            # Group by state
            if state not in state_performance:
                state_performance[state] = {"ratings": [], "stores": [], "reviews": 0}
            state_performance[state]["ratings"].append(insight["avg_rating"])
            state_performance[state]["stores"].append(insight["store_info"]["name"])
            state_performance[state]["reviews"] += insight["total_reviews"]
            
            # Group by city  
            if city not in city_performance:
                city_performance[city] = {"ratings": [], "stores": [], "reviews": 0}
            city_performance[city]["ratings"].append(insight["avg_rating"])
            city_performance[city]["stores"].append(insight["store_info"]["name"])
            city_performance[city]["reviews"] += insight["total_reviews"]
            
            location_data.append({
                "store_name": insight["store_info"]["name"],
                "city": city,
                "state": state,
                "rating": insight["avg_rating"],
                "reviews": insight["total_reviews"],
                "square_footage": insight.get("square_footage", 0),
                "employee_count": insight.get("employee_count", 0)
            })
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Performance by State")
            state_summary = []
            for state, data in state_performance.items():
                avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else 0
                state_summary.append({
                    "State": state,
                    "Avg Rating": f"{avg_rating:.2f}",
                    "Stores": len(data["stores"]),
                    "Total Reviews": data["reviews"]
                })
            
            if state_summary:
                state_df = pd.DataFrame(state_summary)
                st.dataframe(state_df, use_container_width=True)
        
        with col2:
            st.markdown("#### Performance by City")
            city_summary = []
            for city, data in city_performance.items():
                avg_rating = sum(data["ratings"]) / len(data["ratings"]) if data["ratings"] else 0
                city_summary.append({
                    "City": city,
                    "Avg Rating": f"{avg_rating:.2f}",
                    "Stores": len(data["stores"]),
                    "Total Reviews": data["reviews"]
                })
            
            if city_summary:
                city_df = pd.DataFrame(city_summary)
                st.dataframe(city_df, use_container_width=True)
        
        # Store size vs performance correlation
        if location_data:
            st.markdown("#### Store Performance Insights")
            
            # Create scatter plot showing store size vs rating
            location_df = pd.DataFrame(location_data)
            
            fig_scatter = px.scatter(
                location_df, 
                x="square_footage", 
                y="rating",
                size="reviews",
                color="state",
                hover_data=["store_name", "city", "employee_count"],
                title="Store Size vs. Performance",
                labels={
                    "square_footage": "Store Size (sq ft)",
                    "rating": "Average Rating",
                    "reviews": "Total Reviews"
                }
            )
            
            fig_scatter.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#e2e8f0',
                title_font_color='#f1f5f9'
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Regional performance summary
            best_state = max(state_performance.items(), key=lambda x: sum(x[1]["ratings"])/len(x[1]["ratings"]) if x[1]["ratings"] else 0)
            worst_state = min(state_performance.items(), key=lambda x: sum(x[1]["ratings"])/len(x[1]["ratings"]) if x[1]["ratings"] else 0)
            
            st.markdown(f"""
            <div style="background: linear-gradient(145deg, #1e293b 0%, #334155 100%); border: 1px solid #475569; padding: 1rem; border-radius: 10px; margin: 1rem 0;">
                <h5 style="color: #f1f5f9; margin-bottom: 1rem;">📊 Regional Performance Summary</h5>
                <div style="display: flex; gap: 2rem;">
                    <div>
                        <span style="color: #10b981;">🏆 Best Performing State:</span> 
                        <strong style="color: #e2e8f0;">{best_state[0]} ({sum(best_state[1]["ratings"])/len(best_state[1]["ratings"]):.2f} avg)</strong>
                    </div>
                    <div>
                        <span style="color: #f59e0b;">📈 Improvement Opportunity:</span> 
                        <strong style="color: #e2e8f0;">{worst_state[0]} ({sum(worst_state[1]["ratings"])/len(worst_state[1]["ratings"]):.2f} avg)</strong>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Q&A Section
        st.markdown("""
        <div class="qa-container">
            <h3>💬 Ask About This Store</h3>
            <p>Ask specific questions about this store's performance, customer feedback, or recommendations.</p>
        """, unsafe_allow_html=True)
        
        # Example questions
        example_questions = [
            "What are the main complaints from customers?",
            "How can we improve the rating of this store?",
            "What trends are we seeing in recent reviews?",
            "Compare this store to others in the same category.",
            "What is working well at this store?"
        ]
          # Allow user to select from examples or type their own
        user_question = st.text_input(
            "Your question:", 
            key="store_question_ai",
            placeholder="Type your question or select from examples below"
        )
          # Example buttons - using a different approach to avoid session state conflicts
        st.markdown("##### Example Questions")
        cols = st.columns(3)
        
        # Initialize selected question if not exists
        if "selected_question_index" not in st.session_state:
            st.session_state.selected_question_index = None
        
        for i, question in enumerate(example_questions):
            if i % 3 == 0:
                col = cols[0]
            elif i % 3 == 1:
                col = cols[1]
            else:
                col = cols[2]
                
            if col.button(question, key=f"example_{i}"):
                st.session_state.selected_question_index = i
        
        # Determine which question to use
        if st.session_state.selected_question_index is not None:
            question_to_ask = example_questions[st.session_state.selected_question_index]
            # Show which example question was selected
            st.info(f"Selected: {question_to_ask}")
            # Reset the selection after showing
            if st.button("Clear Selection", key="clear_selection"):
                st.session_state.selected_question_index = None
                st.experimental_rerun()
        else:
            question_to_ask = user_question
        
        if st.button("Get Answer", type="primary", use_container_width=True):
            if question_to_ask:
                st.markdown("#### Answer")
                with st.spinner("Analyzing store data..."):
                    answer = data_handler.ask_store_question(selected_insight, question_to_ask)
                    
                    st.markdown(f"""
                    <div class="qa-answer">
                        <div style="margin-bottom: 0.5rem; font-weight: 500; color: #1E40AF;">Q: {user_question}</div>
                        <div>{answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Please enter a question or select one of the examples.")
        
        st.markdown("""
        </div>
        """, unsafe_allow_html=True)
    
    # Footer with last updated timestamp
    st.markdown("""
    <div class="footer">
        <div>© 2023 Williams Sonoma Business Analytics Dashboard</div>
        <div style="font-size: 0.75rem; margin-top: 0.25rem;">Powered by Model Context Protocol</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-refresh functionality
    if auto_refresh:
        time.sleep(15)
        st.rerun()


if __name__ == "__main__":
    main()
