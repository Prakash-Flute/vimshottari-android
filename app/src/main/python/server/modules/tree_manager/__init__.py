#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tree Manager - Disabled for Android
Original functionality: Auto-updates tree.txt when files change
Android: File watching is disabled to save battery and avoid permission issues
"""

import os
import logging

logger = logging.getLogger(__name__)

class TreeManager:
    """TreeManager - Disabled for Android environment"""
    
    def __init__(self):
        self.running = False
        self.thread = None
        
    def generate_tree(self):
        """Generate tree structure - disabled in Android"""
        return "Tree generation disabled in Android"
        
    def count_items(self):
        """Count directories and files - disabled in Android"""
        return 0, 0
    
    def save_tree(self):
        """Save tree to file - disabled in Android"""
        pass
        
    def watch_loop(self):
        """Watch for changes - disabled in Android"""
        pass
    
    def start(self):
        """Start watcher - disabled in Android"""
        logger.info("Tree Manager disabled in Android environment")
        self.running = False
    
    def stop(self):
        """Stop watcher"""
        self.running = False

# Global instance
tree_manager = TreeManager()

# For compatibility with original code
TreeManager = TreeManager
