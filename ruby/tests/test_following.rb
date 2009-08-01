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
    assert_equal(1, BerryMQ::RootTransporter["test_ns1"].size)
  end
end

class Sample2
  include BerryMQ::Follower
  attr_reader :called
  def initialize
    @called = 0
    super
  end
  following("sample2:entry")
  def test_follow_method(message)
    @called += 1
  end
  following("sample2:original")
  def test_original_action(message)
    @called += 1
  end
  following("sample3:entry")
  def test_other_name(message)
    @called +=1
  end
end

class TestMessageSending < Test::Unit::TestCase
  def test_regist
    sample = Sample2.new
    BerryMQ::twitter("sample2:entry")
    assert_equal 1, sample.called
  end

  def test_original_action
    sample = Sample2.new
    BerryMQ::twitter("sample2:original")
    assert_equal 1, sample.called
  end

  def test_wildcard_action_1
    sample = Sample2.new
    BerryMQ::twitter("sample2:*")
    assert_equal 2, sample.called
  end

  def test_wildcard_action_2
    sample = Sample2.new
    BerryMQ::twitter("sample2")
    assert_equal 2, sample.called
  end

  def test_wildcard_name
    sample = Sample2.new
    BerryMQ::twitter("*:entry")
    assert_equal 2, sample.called
  end

  def test_wildcard_all_1
    sample = Sample2.new
    BerryMQ::twitter("*:*")
    assert_equal 3, sample.called
  end

  def test_wildcard_all_2
    sample = Sample2.new
    BerryMQ::twitter("*")
    assert_equal 3, sample.called
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
