require 'berrymq'
require 'test/unit'

class Sample1
  include BerryMQ::Follower
  following("test1@test_ns1:entry")
  def test_follow_method(message)
  end
end

class TestFollowerRegister < Test::Unit::TestCase
  def test_regist
    sample = Sample1.new
    assert_equal(1, BerryMQ::MessageQueueRoot["test_ns1"].size)
  end
end

class Sample2
  include BerryMQ::Follower
  attr_reader :called
  def initialize
    @called = false
    super
  end
  following("test2@test_ns2:entry")
  def test_follow_method(message)
    @called = true
  end
end

class TestMessageSending < Test::Unit::TestCase
  def test_regist
    sample = Sample2.new
    #pp BerryMQ::show_followers
    BerryMQ::twitter("test2@test_ns2:entry")
    assert sample.called
  end
end

class TestUtil < Test::Unit::TestCase
  def test_iter_chain
    a = [1, 2, 3]
    b = [4, 5, 6]
    result = []
    BerryMQ::Util::iter_chain(a, b) { |v|
      result.push(v)
    }
    assert_equal [1, 2, 3, 4, 5, 6], result
  end
end
