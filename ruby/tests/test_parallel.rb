require 'test/unit'
require 'berrymq'

class ThreadPoolTest < Test::Unit::TestCase
  def test_create1
    assert_raise(ArgumentError) do
      BerryMQ::ThreadPool::make_thread_pool(-1)
    end
  end

  def test_create2
    BerryMQ::ThreadPool::make_thread_pool(5)
    assert_equal(5, BerryMQ::ThreadPool::thread_count)
    assert(!BerryMQ::ThreadPool::empty?)
    BerryMQ::ThreadPool::stop_thread_pool()
    assert_equal(0, BerryMQ::ThreadPool::thread_count)
    assert(BerryMQ::ThreadPool::empty?)
  end

  def test_recreate2
    BerryMQ::ThreadPool::make_thread_pool(3)
    assert_equal(3, BerryMQ::ThreadPool::thread_count)
    assert(!BerryMQ::ThreadPool::empty?)
    BerryMQ::ThreadPool::make_thread_pool(5)
    assert_equal(5, BerryMQ::ThreadPool::thread_count)
    assert(!BerryMQ::ThreadPool::empty?)
    BerryMQ::ThreadPool::stop_thread_pool()
    assert_equal(0, BerryMQ::ThreadPool::thread_count)
    assert(BerryMQ::ThreadPool::empty?)
  end

  def test_recreate3
    BerryMQ::ThreadPool::make_thread_pool(5)
    assert_equal(5, BerryMQ::ThreadPool::thread_count)
    assert(!BerryMQ::ThreadPool::empty?)
    BerryMQ::ThreadPool::make_thread_pool(3)
    sleep(1)
    assert_equal(3, BerryMQ::ThreadPool::thread_count)
    assert(!BerryMQ::ThreadPool::empty?)
    BerryMQ::ThreadPool::stop_thread_pool()
    assert_equal(0, BerryMQ::ThreadPool::thread_count)
    assert(BerryMQ::ThreadPool::empty?)
  end
end
