$LOAD_PATH.unshift(File::expand_path(File::dirname(__FILE__)) + '/../lib')

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


class Sample4
  include BerryMQ::Follower
  def initialize(history)
    @call_history = history
    super()
  end

  auto_twitter("sample4:entry")
  def twitt_entry_method
    @call_history.push("target")
  end

  auto_twitter("sample4:exit")
  def twitt_exit_method
    @call_history.push("target")
  end

  auto_twitter("sample4")
  def twitter_entry_and_exit_method
    @call_history.push("target")
  end

  following("sample4:entry")
  def follow_entry(message)
    @call_history.push("entry")
  end

  following("sample4:exit")
  def follow_exit(message)
    @call_history.push("exit")
  end
end

class TestAutoTwitter < Test::Unit::TestCase
  def test_auto_twitter_enter
    call_history = []
    sample = Sample4.new(call_history)
    sample.twitt_entry_method
    assert_equal ["entry", "target"], call_history
  end

  def test_auto_twitter_exit
    call_history = []
    sample = Sample4.new(call_history)
    sample.twitt_exit_method
    assert_equal ["target", "exit"], call_history
  end

  def test_auto_twitter_both
    call_history = []
    sample = Sample4.new(call_history)
    sample.twitter_entry_and_exit_method
    assert_equal ["entry", "target", "exit"], call_history
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


