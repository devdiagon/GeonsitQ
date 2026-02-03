import pytest
import pickle
import time
from pathlib import Path
from datetime import datetime, timedelta

from utils.cache_manager import CacheManager


@pytest.mark.unit
@pytest.mark.cache
class TestCacheManager:
  def test_initialization(self, tmp_path):
    cache_mgr = CacheManager(
      cache_dir=str(tmp_path),
      ttl_hours=1
    )
    
    assert cache_mgr.cache_dir == tmp_path
    assert cache_mgr.ttl_hours == 1
    assert tmp_path.exists()
    
  def test_set_and_get(self, mock_cache_manager):
    test_data = {'key': 'value', 'number': 42}
    
    success = mock_cache_manager.set(
        identifier='test_cache',
        data=test_data
    )
    
    assert success is True
    
    retrieved = mock_cache_manager.get(
      identifier='test_cache'
    )
    
    assert retrieved == test_data
    
  def test_set_with_params(self, mock_cache_manager):
    data1 = {'value': 1}
    data2 = {'value': 2}
    
    mock_cache_manager.set('test', data1, params={'param': 'A'})
    mock_cache_manager.set('test', data2, params={'param': 'B'})
    
    retrieved1 = mock_cache_manager.get('test', params={'param': 'A'})
    retrieved2 = mock_cache_manager.get('test', params={'param': 'B'})
    
    assert retrieved1 == data1
    assert retrieved2 == data2
    
  def test_get_nonexistent(self, mock_cache_manager):
    result = mock_cache_manager.get('nonexistent')
    
    assert result is None
    
  def test_ttl_expiration(self, tmp_path):
    cache_mgr = CacheManager(
      cache_dir=str(tmp_path),
      ttl_hours=0.0001
    )
    
    cache_mgr.set('test', {'data': 'test'})
    
    time.sleep(0.5)
    
    retrieved = cache_mgr.get('test')
    
    assert retrieved is None
    
  def test_set_with_metadata(self, mock_cache_manager):
    data = {'test': 'data'}
    metadata = {'created_by': 'test', 'version': '1.0'}
      
    mock_cache_manager.set(
      'test',
      data,
      metadata=metadata
    )
      
    retrieved = mock_cache_manager.get('test')
    
    assert retrieved == data
    
  def test_validator(self, mock_cache_manager):
    data = {'value': 100}
    
    mock_cache_manager.set('test', data)
    
    def validator(d):
      return d.get('value', 0) <= 50
    
    result = mock_cache_manager.get('test', validator=validator)
    
    assert result is None
    
  def test_invalidate(self, mock_cache_manager):
    mock_cache_manager.set('test', {'data': 'test'})
    
    success = mock_cache_manager.invalidate('test')
    
    assert success is True
    
    retrieved = mock_cache_manager.get('test')
    assert retrieved is None
    
  def test_invalidate_nonexistent(self, mock_cache_manager):
    success = mock_cache_manager.invalidate('nonexistent')
    
    assert success is False
    
  def test_clear_all(self, tmp_path):
    cache_mgr = CacheManager(cache_dir=str(tmp_path))
    
    cache_mgr.set('cache1', {'data': 1})
    cache_mgr.set('cache2', {'data': 2})
    cache_mgr.set('cache3', {'data': 3})
    
    count = cache_mgr.clear_all()
    
    assert count == 3
    assert cache_mgr.get('cache1') is None
    assert cache_mgr.get('cache2') is None
    assert cache_mgr.get('cache3') is None
    
  def test_cleanup_expired(self, tmp_path):
    cache_mgr = CacheManager(
      cache_dir=str(tmp_path),
      ttl_hours=0.0001
    )
    
    cache_mgr.set('cache1', {'data': 1})
    cache_mgr.set('cache2', {'data': 2})
    
    time.sleep(0.5)
    
    count = cache_mgr.cleanup_expired()
    
    assert count == 2
    
  def test_get_stats(self, tmp_path):
    cache_mgr = CacheManager(cache_dir=str(tmp_path))
    
    cache_mgr.set('cache1', {'data': 1})
    cache_mgr.set('cache2', {'data': 2})
    
    stats = cache_mgr.get_stats()
    
    assert 'total_files' in stats
    assert 'valid_files' in stats
    assert 'expired_files' in stats
    assert 'total_size_mb' in stats
    assert stats['total_files'] == 2
    assert stats['valid_files'] == 2
    
  def test_generate_key_consistency(self, mock_cache_manager):
    params = {'a': 1, 'b': 2}
    
    key1 = mock_cache_manager._generate_key('test', params)
    key2 = mock_cache_manager._generate_key('test', params)
    
    assert key1 == key2
    
  def test_generate_key_different_params(self, mock_cache_manager):
    key1 = mock_cache_manager._generate_key('test', {'a': 1})
    key2 = mock_cache_manager._generate_key('test', {'a': 2})
    
    assert key1 != key2
    
  def test_version_mismatch(self, tmp_path):
    cache_mgr_v1 = CacheManager(
      cache_dir=str(tmp_path),
      version='1.0.0'
    )
    
    cache_mgr_v1.set('test', {'data': 'test'})
    
    cache_mgr_v2 = CacheManager(
      cache_dir=str(tmp_path),
      version='2.0.0'
    )
    
    result = cache_mgr_v2.get('test')
    
    assert result is None