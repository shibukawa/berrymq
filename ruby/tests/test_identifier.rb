require 'test/unit'
require 'berrymq'

class IdentiferTest < Test::Unit::TestCase
  def test_match
    exposer = BerryMQ::Identifier.new("id_sample1:entry")
    follower = BerryMQ::Identifier.new("id_sample1:entry")
    assert follower.is_match(exposer)
  end

  def test_match_only_name
    exposer = BerryMQ::Identifier.new("id_sample2")
    follower = BerryMQ::Identifier.new("id_sample2:entry")
    assert follower.is_match(exposer)
  end

  def test_wildcard_action
    exposer = BerryMQ::Identifier.new("id_sample3:test")
    follower = BerryMQ::Identifier.new("id_sample3:*")
    assert follower.is_match(exposer)
  end

  def test_wildcard_name
    exposer = BerryMQ::Identifier.new("id_sample4:entry")
    follower = BerryMQ::Identifier.new("*:entry")
    assert follower.is_match(exposer)
  end

  def test_wildcard_all_1
    exposer = BerryMQ::Identifier.new("id_sample5:entry")
    follower = BerryMQ::Identifier.new("*:*") 
    assert follower.is_match(exposer)
  end

  def test_wildcard_all_2
    exposer = BerryMQ::Identifier.new("id_sample6:entry")
    follower = BerryMQ::Identifier.new("*") 
    assert follower.is_match(exposer)
  end

  def test_local_namespace
    exposer = BerryMQ::Identifier.new("_id_sample7:entry")
    assert exposer.is_local
  end

  def test_namespace
    exposer = BerryMQ::Identifier.new("id_sample8@layer:entry")
    follower = BerryMQ::Identifier.new("*@layer:entry")
    assert_equal "layer", exposer.namespace
    assert_equal "layer", follower.namespace
  end
end

